from mesa import Model
from mesa.space import ContinuousSpace
from mesa.time import RandomActivation
from model_cells import CellAgent
import random


class ProcessModel(Model):

    def __init__(self, initial_densities, width, height, density_radius=(1, 1, 1), frequency_radius=(1, 1, 1),
                 dispersal_radius=(1, 1, 1), max_cells_per_unit=10, deterministic_death=True, age_limit=20,
                 death_ratio=0.2, death_period_limit=0, birth_rates=(0.2, 0.2, 0.2), k=25, l=20, a=1):

        super().__init__()

        self.num_selfish, self.num_cooperative, self.num_tkiller = initial_densities
        self.num_tumor_cells = self.num_selfish + self.num_cooperative
        self.num_total = self.num_tumor_cells + self.num_tkiller

        self.space = ContinuousSpace(width, height, True)
        self.schedule = RandomActivation(self)

        self.density_radius = density_radius
        self.frequency_radius = frequency_radius
        self.dispersal_radius = dispersal_radius

        self.max_cells_per_unit = max_cells_per_unit
        self.deterministic_death = deterministic_death
        self.age_limit = age_limit
        self.death_ratio = death_ratio
        self.death_period_limit = death_period_limit
        self.birth_rates = birth_rates
        self.k, self.l, self.a = k, l, a

        self.cells2add = []
        self.cells2delete = []
        self.all_cell_pos = [[], []]
        self.pos_selfish_cells = [[], []]
        self.pos_cooperative_cells = [[], []]
        self.pos_tkiller_cells = [[], []]
        self.pos_dead_cells = [[], []]

        added_selfish, added_cooperative, added_tkiller = 0, 0, 0
        random.seed(100)

        def n_cells():
            return added_selfish + added_cooperative + added_tkiller

        mortality_rates = [random.uniform(0, 0.2), random.uniform(0, 0.2), random.uniform(0, 0.2)]
        while n_cells() < self.num_total:

            rnd_i = random.randrange(3)

            if rnd_i == 0 and added_selfish < self.num_selfish:
                a = CellAgent(n_cells(), self, rnd_i)
                a.set_gamma(0.1)
                a.set_epsilon(0.7)
                a.set_d(mortality_rates[0])
                added_selfish += 1

            elif rnd_i == 1 and added_cooperative < self.num_cooperative:
                a = CellAgent(n_cells(), self, rnd_i)
                a.set_gamma(0.1)
                a.set_epsilon(0.7)
                a.set_d(mortality_rates[1])
                added_cooperative += 1

            elif rnd_i == 2 and added_tkiller < self.num_tkiller:
                a = CellAgent(n_cells(), self, rnd_i)
                a.set_gamma(0.1)
                a.set_delta(0.001)
                a.set_d(mortality_rates[2])
                added_tkiller += 1

            else:
                continue

            self.schedule.add(a)
            center_width_min = self.space.center[0] - (0.2 * self.space.width)
            center_width_max = self.space.center[0] + (0.2 * self.space.width)
            center_height_min = self.space.center[1] - (0.2 * self.space.height)
            center_height_max = self.space.center[1] + (0.2 * self.space.height)

            # Add the agent to a random pos
            x = random.uniform(center_width_min, center_width_max)
            y = random.uniform(center_height_min, center_height_max)

            self.space.place_agent(a, (x, y))

        self.counter = 0

    @property
    def g(self):
        density = self.get_density()
        if density[0] + density[1] == 0:
            return 0
        return density[1]/(density[0] + density[1])

    def get_density(self, agents=None):
        density = [0, 0, 0]
        if agents is None:
            agents = self.schedule.agents
        for cell in agents:
            density[cell.type] += 1
        return density

    def new_cell2add(self, cell):
        if not self.cells2add.__contains__(cell):
            self.cells2add.append(cell)

    def new_cell2delete(self, cell):
        if not self.cells2delete.__contains__(cell):
            self.cells2delete.append(cell)

    def add_cell_pos(self, pos, cell_type):

        if cell_type == 0:
            self.pos_selfish_cells[0].append(pos[0])
            self.pos_selfish_cells[1].append(pos[1])
        elif cell_type == 1:
            self.pos_cooperative_cells[0].append(pos[0])
            self.pos_cooperative_cells[1].append(pos[1])
        elif cell_type == 2:
            self.pos_tkiller_cells[0].append(pos[0])
            self.pos_tkiller_cells[1].append(pos[1])
        else:
            return

    def clear_all_cell_pos(self):
        self.pos_selfish_cells = [[], []]
        self.pos_cooperative_cells = [[], []]
        self.pos_tkiller_cells = [[], []]

    def step(self):

        self.schedule.step()
        self.counter = 0

    def add_new_cells(self):
        for c, p in self.cells2add:
            self.schedule.add(c)
            self.space.place_agent(c, p)
            self.add_cell_pos(p, c.type)
            self.cells2add.remove((c, p))

    def delete_dead_cells(self):

        for c in self.cells2delete:

            removed_x, removed_y = False, False
            if c.type == 0:
                if self.pos_selfish_cells[0].__contains__(c.pos[0]):
                    self.pos_selfish_cells[0].remove(c.pos[0])

                if self.pos_selfish_cells[1].__contains__(c.pos[1]):
                    self.pos_selfish_cells[1].remove(c.pos[1])
                    removed_y = True
            elif c.type == 1:
                if self.pos_cooperative_cells[0].__contains__(c.pos[0]):
                    self.pos_cooperative_cells[0].remove(c.pos[0])
                    removed_x = True
                if self.pos_cooperative_cells[1].__contains__(c.pos[1]):
                    self.pos_cooperative_cells[1].remove(c.pos[1])
                    removed_y = True
            elif c.type == 2:
                if self.pos_tkiller_cells[0].__contains__(c.pos[0]):
                    self.pos_tkiller_cells[0].remove(c.pos[0])
                    removed_x = True
                if self.pos_tkiller_cells[1].__contains__(c.pos[1]):
                    self.pos_tkiller_cells[1].remove(c.pos[1])
                    removed_y = True

            self.schedule.remove(c)
            self.cells2delete.remove(c)