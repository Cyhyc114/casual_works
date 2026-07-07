# translator.py
from .get_codons import CodonDatabase

WINDOW_SIZE_AA = 20
STEP_SIZE_AA = 10
GC_MARGIN = 0.02          # Soft margin for window GC check (±2%)
FINAL_GC_MARGIN = 0.03    # Soft margin for final GC audit (±3%)


def translate(
    species: str,
    protein: str,
    avoid: list[str] | None = None,
    gc_min: float = 0.4,
    gc_max: float = 0.6
) -> dict:
    """
    Reverse-translate with local window optimization.

    - Codons are chosen by highest frequency (max CAI) first.
    - Hard constraint: avoid forbidden motifs.
    - Soft constraint: GC content of the last WINDOW_SIZE_AA codons must stay
      within [gc_min - GC_MARGIN, gc_max + GC_MARGIN] when checked every STEP_SIZE_AA codons.
    - When a window fails the soft constraint, we adjust the entire window to
      bring it within the soft margin (using bidirectional GC-aware replacement).
    - Final audit: if final GC is outside [gc_min, gc_max] but within margin, a warning is issued
      (not an error). If outside margin, a stronger warning is issued.
    """
    db = CodonDatabase()
    codon_table = db.tables[species]
    protein = protein.upper()
    avoid = avoid or []
    dna_list = []
    codon_freq_list = []          # track frequencies of chosen codons
    total_compromise = 0
    warnings = []

    # ---------- Helper functions ----------
    def gc_of_codon(codon: str) -> float:
        """Return GC ratio (0-1) for a single codon."""
        return (codon.count('G') + codon.count('C')) / 3.0

    def gc_ratio_of_codons(codons: list[str]) -> float:
        """Compute GC ratio (0-1) for a list of codons."""
        dna = "".join(codons)
        if not dna:
            return 0.5
        gc = dna.count("G") + dna.count("C")
        return gc / len(dna)

    def adjust_window(
        codons: list[str],
        freqs: list[float],
        start_idx: int,
        protein_seq: str,
        codon_table: dict,
        avoid_list: list[str],
        gmin: float,
        gmax: float
    ) -> tuple[list[str], list[float], bool]:
        """
        Attempt to adjust codons from start_idx to the end (entire window) to bring
        the last WINDOW_SIZE_AA window GC into the soft margin.

        The algorithm:
          1. Calculates current window GC.
          2. If too high, tries to replace codons with lower-GC alternatives.
          3. If too low, tries to replace with higher-GC alternatives.
          4. For each position, candidates are sorted by GC distance from current,
             but we also consider frequency as a secondary criterion (preferring
             higher frequency among those with similar GC).
          5. Always verifies that no avoid motif is introduced.
          6. Returns (new_codons, new_freqs, success) if a valid configuration is found.
        """
        new_codons = codons[:]
        new_freqs = freqs[:]
        target_indices = list(range(start_idx, len(new_codons)))
        if not target_indices:
            return new_codons, new_freqs, False

        # Current window (last WINDOW_SIZE_AA codons, or all if shorter)
        window_codons = new_codons[-WINDOW_SIZE_AA:] if len(new_codons) >= WINDOW_SIZE_AA else new_codons
        current_gc = gc_ratio_of_codons(window_codons)
        target_low = gmin - GC_MARGIN
        target_high = gmax + GC_MARGIN

        # Determine adjustment direction
        need_higher_gc = current_gc < target_low
        need_lower_gc = current_gc > target_high

        # If already within margin, no adjustment needed
        if not need_higher_gc and not need_lower_gc:
            return new_codons, new_freqs, True

        # Helper: get candidate codons for an amino acid, sorted by GC preference
        def get_candidates(aa: str, prefer_higher: bool) -> list[tuple[str, float]]:
            freq_dict = codon_table[aa]
            items = list(freq_dict.items())  # (codon, freq)
            # Sort by GC ratio, then by frequency (higher freq preferred within same GC)
            items.sort(key=lambda x: (gc_of_codon(x[0]), -x[1]))
            if prefer_higher:
                items.reverse()
            return items

        # Greedy single pass over positions (we could repeat for better results)
        for pos in target_indices:
            aa = protein_seq[pos]
            current_codon = new_codons[pos]
            # Get candidates that could improve GC
            candidates = get_candidates(aa, prefer_higher=need_higher_gc)
            for cand_codon, cand_freq in candidates:
                if cand_codon == current_codon:
                    continue
                # Test if using this candidate would still respect avoid motifs
                test_codons = new_codons[:pos] + [cand_codon] + new_codons[pos+1:]
                test_dna = "".join(test_codons)
                if avoid_list and any(motif in test_dna for motif in avoid_list):
                    continue

                # Check if the change brings window GC within soft margin
                new_window_codons = test_codons[-WINDOW_SIZE_AA:] if len(test_codons) >= WINDOW_SIZE_AA else test_codons
                new_gc = gc_ratio_of_codons(new_window_codons)

                if target_low <= new_gc <= target_high:
                    # Successfully brought within margin
                    new_codons[pos] = cand_codon
                    new_freqs[pos] = cand_freq
                    return new_codons, new_freqs, True
                # If not within margin but moves in right direction, we could accept and continue,
                # but for simplicity we only accept if it directly meets the margin.
                # In a more advanced version, we could allow incremental improvements.
        # If no single change works, we could try combinations (not implemented here)
        return new_codons, new_freqs, False

    # ---------- Main translation loop ----------
    for idx, aa in enumerate(protein, start=1):
        try:
            freq_dict = codon_table[aa]
        except KeyError:
            raise ValueError(f"Invalid amino acid '{aa}' in sequence")

        sorted_codons = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)
        chosen_codon = None
        chosen_freq = 0.0

        # Try to pick the best codon satisfying "avoid" constraint
        for codon, freq in sorted_codons:
            temp_dna = "".join(dna_list) + codon
            if avoid and any(motif in temp_dna for motif in avoid):
                continue
            chosen_codon = codon
            chosen_freq = freq
            break

        if chosen_codon is None:
            raise ValueError(f"No codon available for '{aa}' avoiding {avoid}")

        dna_list.append(chosen_codon)
        codon_freq_list.append(chosen_freq)

        # ---- GC checkpoint (every STEP_SIZE_AA codons or at end) ----
        if idx % STEP_SIZE_AA == 0 or idx == len(protein):
            # Get the last WINDOW_SIZE_AA codons (or all if shorter)
            window_codons = dna_list[-WINDOW_SIZE_AA:] if len(dna_list) >= WINDOW_SIZE_AA else dna_list
            current_gc = gc_ratio_of_codons(window_codons)

            # If window GC is outside the soft margin, try to adjust
            if not (gc_min - GC_MARGIN <= current_gc <= gc_max + GC_MARGIN):
                # Adjust the entire window (start at window start)
                adjust_start = max(0, len(dna_list) - WINDOW_SIZE_AA)
                new_dna_list, new_freq_list, success = adjust_window(
                    dna_list,
                    codon_freq_list,
                    adjust_start,
                    protein,
                    codon_table,
                    avoid,
                    gc_min,
                    gc_max
                )
                if success:
                    # Count compromises (number of positions changed)
                    for i in range(adjust_start, len(dna_list)):
                        if dna_list[i] != new_dna_list[i]:
                            total_compromise += 1
                    dna_list = new_dna_list
                    codon_freq_list = new_freq_list
                    # Verify the window GC is now within soft margin
                    new_window = dna_list[-WINDOW_SIZE_AA:] if len(dna_list) >= WINDOW_SIZE_AA else dna_list
                    new_gc = gc_ratio_of_codons(new_window)
                    if not (gc_min - GC_MARGIN <= new_gc <= gc_max + GC_MARGIN):
                        raise ValueError(
                            f"Unable to adjust window to meet soft GC margin. "
                            f"Window GC={new_gc:.2f}, target margin "
                            f"[{gc_min - GC_MARGIN:.2f}, {gc_max + GC_MARGIN:.2f}]. "
                            "Please relax constraints."
                        )
                else:
                    raise ValueError(
                        f"Window GC {current_gc:.2f} outside soft margin "
                        f"[{gc_min - GC_MARGIN:.2f}, {gc_max + GC_MARGIN:.2f}] "
                        "and adjustment failed. Please relax constraints."
                    )

    # ---------- Final audit (warnings only, not errors) ----------
    final_dna = "".join(dna_list)
    final_gc = (final_dna.count('G') + final_dna.count('C')) / len(final_dna)

    # Check against strict target range
    if final_gc < gc_min or final_gc > gc_max:
        warnings.append(
            f"Final GC ({final_gc:.1%}) is outside the target range "
            f"({gc_min:.0%} - {gc_max:.0%})."
        )
    # Check against final margin
    if final_gc < gc_min - FINAL_GC_MARGIN or final_gc > gc_max + FINAL_GC_MARGIN:
        warnings.append(
            f"Final GC ({final_gc:.1%}) exceeds the acceptable margin "
            f"({gc_min - FINAL_GC_MARGIN:.0%} - {gc_max + FINAL_GC_MARGIN:.0%})."
        )

    return {
        "dna": final_dna,
        "gc_percent": final_gc * 100,      # percentage for display
        "length": len(final_dna),
        "compromises": total_compromise,
        "status": "warning" if warnings else "success",
        "warnings": warnings
    }