import pile as pl
from report import Report, ReportPile

a = pl.Soil()

p1 = pl.Pile_mc_zk(a, 1.2, 17.5)
p2 = pl.Pile_dc(a, 1.2, 17.5)
rw1 = ReportPile('0_pile_test')
rw1.set_format2()
rw1.pile_report(p1, p2, 4200)
rw1.tex_out()


# p2 = pl.Pile_mc_cz(a, 1.2, 17.5)


# p = [p1, p2, p3]
# for i in p:
#     if hasattr(i, 'ra3'):
#         print(f'土体侧摩阻：{i.ra1}')
#         print(f'岩石侧摩阻：{i.ra2}')
#         print(f'端承力：{i.ra3}')
#         print(f'单桩承载力：{i.ra0}')
#         print(f'去除自重差承载力：{i.ra}\n')
#     else:
#         print(f'土体侧摩阻：{i.ra1}')
#         print(f'端承力：{i.ra2}')
#         print(f'单桩承载力：{i.ra0}')
#         print(f'去除自重差承载力：{i.ra}\n')


# # ll = np.linspace(0, 17.5, 200)
# ll = pl.get_l(a, 1.2, 4001)
# pl.pile_l(ll, a, 1.2, 4001)