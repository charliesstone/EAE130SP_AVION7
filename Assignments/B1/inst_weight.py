def instruments_weight(N_en, N_t, N_ci):
    if N_en <= 0 or N_t <= 0 or N_ci <= 0:
        raise ValueError("All inputs must be positive.")

    W_instruments = (
        8.0
        + 36.37 * (N_en ** 0.676) * (N_t ** 0.237)
        + 26.4 * ((1 + N_ci) ** 1.356)
    )

    return W_instruments


N_en = 1      # single engine
N_t = 3       # 1 fuselage tank + 2 wing tanks
N_ci = 1.0    # single pilot

W_inst = instruments_weight(N_en, N_t, N_ci)
print(f"Instrument weight = {W_inst:.2f} lb")