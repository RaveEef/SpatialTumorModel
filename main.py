from model_process import ProcessModel
from matplotlib import pyplot as plt

import imageio
import glob
import re
import os


# PARAMETERS
# Significance level for difference in growthrates for selfish, cooperative, and tkiller cell respectively
SIGNIFICANCE_EQ_GROWTH_RATE = [0.05, 0.05, 0.05]
# for file in os.listdir('figures\\'):
#   os.remove('figures\\'+ file)

numbers = re.compile(r"(\d+)")


def numerical_sort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


def scatter_plot(i, model, initial_densities):

    selfish = plt.scatter(model.pos_selfish_cells[0], model.pos_selfish_cells[1], c='r', s=2, label='Selfish Cells')
    cooperative = plt.scatter(model.pos_cooperative_cells[0], model.pos_cooperative_cells[1], c='b', s=2,
                              label='Cooperative Cells')
    tkiller = plt.scatter(model.pos_tkiller_cells[0], model.pos_tkiller_cells[1], c='g', s=2, label="T-Killer Cells")
    plt.xlim(0, model.space.width)
    plt.ylim(0, model.space.height)
    plt.title("Iteration {}, Initial Density: [{}, {}, {}]".format(i, initial_densities[0],
                                                                   initial_densities[1], initial_densities[2]))
    if initial_densities[0] == 0:
        plt.legend(handles=[cooperative, tkiller])
    elif initial_densities[1] == 0:
        plt.legend(handles=[selfish, tkiller])
    else:
        plt.legend(handles=[selfish, cooperative, tkiller])

    directory = "figures_{}_{}_{}".format(initial_densities[0], initial_densities[1], initial_densities[2])
    if not os.path.exists(directory):
        os.makedirs(directory)

    plt.savefig("figures_{}_{}_{}\\fig{}.jpg".format(initial_densities[0], initial_densities[1], initial_densities[2], i))
    plt.gcf().clear()


def files_ordered(folder):
    ordered_files = []
    for infile in sorted(glob.glob('{}\\*.jpg'.format(folder)), key=numerical_sort):
        ordered_files.append(infile)
    print(ordered_files)
    return ordered_files


def make_gif(initial_density):

    folder = "figures_{}_{}_{}".format(initial_density[0], initial_density[1], initial_density[2])
    with imageio.get_writer('process.gif', mode='I') as writer:
        files = files_ordered(folder)
        for filename in files:

            image = imageio.imread(filename)
            writer.append_data(image)

    gif = imageio.mimread('process.gif')

    imageio.mimsave('process_{}_{}_{}.gif'.format(initial_density[0], initial_density[1], initial_density[2]),
                    gif, fps=(len(files)/10))

    if os.path.isfile("process.gif"):
        os.remove("process.gif")


def run(initial_density, n_iteration=100, plot_frequency=1):

    model = ProcessModel(initial_density, 50, 50)

    density_stable_counter = [0, 0, 0]
    growth_rate_stable_counter = [0, 0, 0]
    before_growth_rates = [0, 0, 0]

    for i in range(n_iteration):

        print("i: ", i)

        model.clear_all_cell_pos()
        if len(model.schedule.agents) == 0:
            break

        before_densities = model.get_density()

        model.step()
        for c in model.schedule.agents:
            model.add_cell_pos(c.pos, c.type)

        added_types = model.add_new_cells()
        print("Added selfish: {}\nAdded coop: {}\nAdded tkiller: {}".format(added_types[0], added_types[1],
                                                                            added_types[2]))

        dead_types = model.delete_dead_cells()
        print("Dead selfish: {}\nDead coop: {}\nDead tkiller: {}".format(dead_types[0], dead_types[1], dead_types[2]))

        if plot_frequency > 0 and i % plot_frequency == 0:
            scatter_plot(i, model, initial_density)

        after_densities = model.get_density()
        diff_densities = [abs(before_densities[0] - after_densities[0]), abs(before_densities[1] - after_densities[1]),
                          abs(before_densities[2] - after_densities[2])]

        def growth_rate(before, after):
            if before == 0:
                return after - before
            return (after - before)/before

        after_growth_rates = [growth_rate(before_densities[0], after_densities[0]),
                        growth_rate(before_densities[1], after_densities[1]),
                              growth_rate(before_densities[2], after_densities[2])]
        diff_growth_rates = [abs(before_growth_rates[0] - after_growth_rates[0]),
                                 abs(before_growth_rates[1] - after_growth_rates[1]),
                             abs(before_growth_rates[2] - after_growth_rates[1])]

        if diff_densities[0] <= (0.05 * initial_density[0]):
            density_stable_counter[0] += 1
        else:
            density_stable_counter[0] = 0

        if diff_densities[1] <= (0.05 * initial_density[1]):
            density_stable_counter[1] += 1
        else:
            density_stable_counter[1] = 0

        if diff_densities[2] <= (0.05 * initial_density[2]):
            density_stable_counter[2] += 1
        else:
            density_stable_counter[2] = 0

        if diff_growth_rates[0] <= 0.05:
            growth_rate_stable_counter[0] += 1
        else:
            growth_rate_stable_counter[0] = 0

        if diff_growth_rates[1] <= 0.05:
            growth_rate_stable_counter[1] += 1
        else:
            growth_rate_stable_counter[1] = 0

        if diff_growth_rates[2] <= 0.05:
            growth_rate_stable_counter[2] += 1
        else:
            growth_rate_stable_counter[2] = 0

        print("difference densities: {} and stability_counter: {}".format(diff_densities, density_stable_counter))
        print("difference growth rates: {} and stability counter: {}".format(diff_growth_rates,
                                                                             growth_rate_stable_counter))

        if density_stable_counter[0] > 10 and density_stable_counter[1] > 10 and density_stable_counter[2] > 10:
            print("EQ density")
            break
        if growth_rate_stable_counter[0] > 10 and growth_rate_stable_counter[1] > 10 and growth_rate_stable_counter[2] > 10:
            print("EQ growth rate")
            break

        before_growth_rates = after_growth_rates



    make_gif(initial_density)

from egtplot import plot_static


initial_densities = [[50, 50, 50]]

def get_payoff(alpha, beta, gamma, rho):
    return [[0, alpha, 0],
            [1 + alpha - beta, 1 - 2 * beta, 1 - beta + rho],
            [1 - gamma, 1 - gamma, 1 - gamma]]


if __name__ == "__main__":
    # for id in initial_densities:
    #    run(id, n_iteration=100, plot_frequency=0)
    parameter_values = [[1], [1], [1], [1]]
    labels = ['S', 'D', 'I']
    # simplex = plot_static(parameter_values, custom_func=get_payoff, vert_labels=labels)
    # payoff_entries = [[0], [-1], [3], [-1], [0], [1], [3], [1], [0]]
    simplex = plot_static(parameter_values, custom_func=get_payoff, vert_labels=labels,
                            paths=True, generations=10, steps=2000, ic_type='random', path_color='viridis')
    plt.show(simplex)
