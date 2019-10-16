from wind import Wind, BeamWind
from report import ReportWind, Report

w1 = Wind(2, 'C', 19.5, 26.6, 1)
bw1 = BeamWind(w1, [6, 2, 30], 100, 80)

w1.get_situation()
w1.get_k()
w1.get_U()

rw1 = ReportWind('0_wind_test')
rw1.set_format2()
rw1.wind_report(bw1, 0)
rw1.tex_out()

