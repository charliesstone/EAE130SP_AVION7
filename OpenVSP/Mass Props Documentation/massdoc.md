# detailing of mass prop documentation into new openvsp model by charlie 03/17/2026

For main components, I'm using the raymer area -> weight assumptions we used in inner_loop.py for the TOGW assumption, the only difference is I'm using slugs in the masses to be consistent with the slugs ft s unit system used in VSP. Also, all the mass properties are for one side of a surface if its mirrored-- this is important for the LERX, Main Wing, HStab, pylons, and some missiles. 

for example: 
## Main Wing
Wing area is 400 ft^2. This is multiplied by 9 as per inner_loop.py to get 3600 lb. This is converted into slugs by multiplying by 1/32.17, which is now ~111 slugs. This has to be normalized to density however, otherwise the cg will be off. As I couldnt find a way to calculate the volume of a shape in openvsp, i approximated-- for the wing, i did the planform area multiplied by the t/c times mean aerodynamic chord to get an approximate wing box volume. This is 400 ft^2 * 11.4 ft * 0.10 = 456 ft^3. Thus, the new density shall be 56 /456 = 0.123 slug/ft^3. This was unsatisfactory (the displayed mass was 37.23 slug), so a correction factor of 111/37.23 ~~ 3 was added, making the new density 0.369. The important thing to note is that the cg of each individual part shouldnt change, since we are assuming isotropic mass groupings. The only thing that should change is the overall cg, since we are changing the relative weights of different components. Major assumptions for all other major parts are now listed:

## Fuselage:
Wetted area: 385.39 * 4.8 (as per inner_loop.py) = 1849.87 lb = 57.5 slug. Fuselage volume approximated as rectangular prism with base of (3.5 ft) (5 ft) = 17.5 ft^2 (XSec 2, a relatively median sized XSec) and height of 43.36, the length of the fuselage. Total volume approximation: 758.8 ft^3. Density approximation: 57.5 / 758.8 =
0.0758 slug/ft^2. As the calculated mass was 54.67 slugs, a correction factor of 57.5/54.7 = 1.05119 was added to get the mass up to 57.47 slug. 

## HStab:
Plan area: 140 ft^2 * 4 = 560 lbm = 17.4 slugs. MAC is 7.29 ft, t/c = 0.10, wing box estimate is 140 * 7.3 * 0.10 = 102.2 ft^3, first density approximation is 0.17 slug/ft^3 (same process as Main Wing is used). This gives 11.7 slugs, correction factor of 17.4/11.7 = 1.487 is applied to get the mass up to 17.44 slug.

## LERX
Plan area: 72 ft^2 * 4 = 288 lb (using same constant as HStab, seeing it sort of like a canard) = 8.95 slug. MAC = 4.67, t/c = 0.07 => box volume assumption = 23.53 ft^3. Density assumption = 8.95/23.53 = 0.34 slug/ft^3. This gives 6.644 slug, correction factor of 8.95/6.64 = 
1.34789 was used to bring mass to 8.955 slug. 

## VStab
Plan area: 140 ft^2 * 5.3 = 742 lb = 23.07 slug. MAC is 7.83 ft, t/c = 0.10, => box volume approximation = 109.62 ft^3 => boxed density approximation => 23.07/109.62 = 0.21 slug/ft^3. This gives mass of 
7.8 slug, correction factor of 2.96 was used to get mass up to 23.08 slug. 

## Engine
The F117 PW-100 dry weight is given to be 5000 lb by P&W. Since the engine is largely placed at y, z = 0 by design, I just placed the C.G. as a point mass of 5000/32.17 = 155.42 slug halfway down the engine in x, at a local coord of 18.333/2 = 9.167 ft (global of 38.12 ft from nose). In order to make sure the engine geometry itself was not calculated, I set the density to zero. As this accounts for total engine weight, I set the densities and all point masses of the other engine components (FADEC, Main Fan, and Diffuser) to zero, effectively nulling them. 

## Wing hardpoints
I couldn't find any data about this online, so I just made some guesses. I figure each pylon is probably able to be lifted by two people, per Navy installation guidelines. This seems like 250 lb-ish for each pylon? So I put a 250lb point mass (7.78 slug) midway between the two. 

## Payloads
For each payload, I took the weight from wikipedia and added a point mass of that weight midway through the length in x in the local coordinates. Listed below are the lengths in x and the masses in lbm and slug for reference:

