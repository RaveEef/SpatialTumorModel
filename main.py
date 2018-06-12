from model_process import ProcessModel
from matplotlib import pyplot as plt
import imageio
import glob
import re
import os

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


def run(initial_density):
    model = ProcessModel(initial_density, 50, 50)

    stability_counter = [0, 0]

    for i in range(42):

        print("i: ", i)

        model.clear_all_cell_pos()
        if len(model.schedule.agents) == 0:
            break

        before_densities = model.get_density()

        model.step()
        for c in model.schedule.agents:
            model.add_cell_pos(c.pos, c.type)
        model.add_new_cells()
        model.delete_dead_cells()

        scatter_plot(i, model, initial_density)

        after_densities = model.get_density()
        diff_densities = [abs(before_densities[0] - after_densities[0]), abs(before_densities[1] - after_densities[1])]

        if diff_densities[0] <= (0.05 * initial_density[0]):
            stability_counter[0] += 1
        else:
            stability_counter[0] = 0
        if diff_densities[1] <= (0.05 * initial_density[1]):
            stability_counter[1] += 1
        else:
            stability_counter[1] = 0

        print("difference densities: {} and stability_counter: {}".format(diff_densities, stability_counter))
        if stability_counter[0] > 10 and stability_counter[1] > 10:
            break

    make_gif(initial_density)


initial_densities = [[20, 20, 20]]

for id in initial_densities:
    run(id)
