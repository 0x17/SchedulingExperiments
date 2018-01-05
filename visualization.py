import utils
import matplotlib.pyplot as plt
from project import adj_mx_to_edges


def plot_revenue_cost_profit_for_makespan(result_dict):
    xs = sorted(list(result_dict.keys()))
    revenues = [result_dict[x]['revenue'] for x in xs]
    costs = [result_dict[x]['oc'] for x in xs]
    profits = [result_dict[x]['obj'] for x in xs]
    plt.plot(xs, revenues, label='revenues')
    plt.plot(xs, costs, label='costs')
    plt.plot(xs, profits, label='profits')
    plt.legend()
    plt.show()


def plot_digraph(p):
    ext = 'pdf'
    out_fn = p.instanceName + '.dot'
    img_fn = p.instanceName + '.'+ext
    ostr = 'digraph {\n'
    for i, j in adj_mx_to_edges(p.adjMx):
        ostr += '{0}->{1}\n'.format(i, j)
    ostr += '}\n'
    utils.spit(ostr, out_fn)
    utils.sys_call('dot -T{0} {1} -o {2}'.format(ext, out_fn, img_fn))
