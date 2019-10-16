from wind import Wind, BeamWind, PierWind

w1 = Wind(2, 'A', 20, 26.6, 2)
bw1 = BeamWind(w1, [6, 2, 30], 80, 80)
pw1 = PierWind(w1, [50, 2, 3, 5, 0.5, 0])

pw2 = PierWind()

pw1.Fg




