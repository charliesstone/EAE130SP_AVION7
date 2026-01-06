import numpy as np
import scipy as sp

avec = np.array([
    1, 2, 3
])
bvec = np.array([
    4, 5, 6
])
npdiag = np.dot(avec, bvec)
f = lambda x: x
spdiag, error = sp.integrate.quad(f, 0, 1)


print(f"""
Charlie Stone
SSID: 920605938
Windows 11 build 26100.7462
if a_vec = [1, 2, 3]
and b_vec = [4, 5, 6]
and scipy int_eval = integral(x) from 0 - 1
scipy int_eval = {spdiag}
numpy dot product = {npdiag}
""")

