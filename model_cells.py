from mesa import Agent
import random
from math import pi, sqrt


class CellAgent(Agent):
    """ An agent with fixed initial wealth."""

    def __init__(self, unique_id, model, cell_type):
        super().__init__(unique_id, model)

        self.age = -1
        self.type = cell_type
        self.state = 1
        self.death_period = -1

        self.wealth = 1
        self.pos = None

        self.gamma = None
        self.epsilon = None
        self.delta = None
        self.d = None

    def set_gamma(self, gamma):
        self.gamma = gamma

    def set_epsilon(self, epsilon):
        self.epsilon = epsilon

    def set_delta(self, delta):
        self.delta = delta

    def set_d(self, d):
        self.d = d

    def cell_info(self):
        print("ID: {}, type: {}, pos: {}, state: {}, age: {}".format(
                    self.unique_id, self.type, self.pos, self.state, self.age))

    def is_alive(self):
        if self.state == 1:
            return True
        return False

    def is_dead(self):
        if self.state == 0:
            return True
        return False

    def deterministic_death(self):
        self.age += 1
        if self.age >= self.model.age_limit:
            self.state = 0
            self.model.new_cell2delete.append(self)

    def stochastic_death(self):
        if random.random() <= self.model.death_ratio:
            self.state = 0
            self.model.new_cell2delete(self)

    def get_neighbours(self, radius):
        return self.model.space.get_neighbors(self.pos, radius, False)

    def is_crowed(self, neighbours):

        if len(neighbours) >= (pi * self.model.density_radius[self.type] *
                               self.model.density_radius[self.type] * self.model.max_cells_per_unit):
            return True
        return False

    def give_birth(self):

        neighbours = self.get_neighbours(self.model.density_radius[self.type])
        density = self.model.get_density(neighbours)
        num_cancer = density[0] + density[1]
        num_tkiller = density[2]

        prob_birth = 0
        birth_rate = self.model.birth_rates[self.type]

        if self.type == 0 or self.type == 1:
            prob_birth = 1 - (sqrt(num_cancer) / self.model.k)
            prob_birth = birth_rate * prob_birth
        elif self.type == 2:
            prob_birth = self.model.l + (self.model.a * (sqrt(num_cancer)))
            prob_birth = 1 - (num_tkiller / prob_birth)
            prob_birth = birth_rate * prob_birth
        else:
            print("WHUT")

        rnd_prop = random.uniform(0, 1)
        if prob_birth <= rnd_prop:
            return True
        return False

    def get_real_coord(self, coord_generated, coord_parent, radius):

        w, h = self.model.space.width, self.model.space.height
        coord_x = (coord_generated[0] * radius) + coord_parent[0]
        coord_y = (coord_generated[1] * radius) + coord_parent[1]

        if coord_x < 0:
            coord_x += w
        elif coord_x >= w:
            coord_x -= w
        else:
            "X TROUBLE"

        if coord_y < 0:
            coord_y += h
        elif coord_y >= h:
            coord_y -= h
        else:
            "Y TROUBLE"

        return coord_x, coord_y

    def daughter_cell_pos(self):

        while True:
            x_movement = random.uniform(-self.model.dispersal_radius[self.type], self.model.dispersal_radius[self.type])
            y_movement = random.uniform(-self.model.dispersal_radius[self.type], self.model.dispersal_radius[self.type])
            new_pos = [self.pos[0] + x_movement, self.pos[1] + y_movement]
            if self.model.space.get_distance(self.pos, new_pos) <= 1:
                break

        return new_pos

    def mu(self):
        m = 1 - (self.model.g * self.epsilon)
        return self.gamma * m

    def cell_death(self):

        prob_death = 0
        neighbours = self.get_neighbours(self.model.frequency_radius[self.type])
        density = self.model.get_density(neighbours)
        total_cells = [density[0] + density[1], density[2]]

        if self.type == 0 or self.type == 1:
            if total_cells[0] == 0:
                prob_death = 0
            else:
                prob_death = (1 / total_cells[0]) * (self.mu()) * sqrt(total_cells[0]) * total_cells[1]
                prob_death = self.d + prob_death
        elif self.type == 2:
            prob_death = self.delta * self.model.g * sqrt(total_cells[0])
            prob_death = self.d + prob_death

        if prob_death <= random.uniform(0, 1):
            self.model.new_cell2delete(self)
            return True
        return False

    def step(self):

        self.model.counter += 1
        if self.model.counter % 50 == 0:
            print(self.model.counter, "//", len(self.model.schedule.agents))

        give_birth = self.give_birth()
        if give_birth:
            offspring_pos = self.daughter_cell_pos()
            if self.model.space.out_of_bounds(offspring_pos):
                print(offspring_pos, "out of bounds")
                offspring_pos = self.model.space.torus_adj(offspring_pos)

            offspring = CellAgent(len(self.model.schedule.agents), self.model, self.type)
            offspring.set_gamma(self.gamma)
            offspring.set_delta(self.delta)
            offspring.set_epsilon(self.epsilon)
            offspring.set_d(self.d)

            self.model.new_cell2add((offspring, offspring_pos))

        neighbours = self.get_neighbours(self.model.density_radius[self.type])
        str_neighbours = "["
        for n in neighbours:
            if len(str_neighbours) == 1:
                str_neighbours = str_neighbours + str(n.unique_id)
            else:
                str_neighbours = str_neighbours + ", " + str(n.unique_id)
        str_neighbours += "]"

        if self.cell_death():
            self.state = 0
            self.model.new_cell2delete(self)
            # self.model.add_cell_pos(self.pos, -1)
        else:
            self.model.add_cell_pos(self.pos, self.type)



'''class CellAgent(Agent):

    def __init__(self, unique_id, model, cell_type):

        super().__init__(unique_id, model)

        self.age = -1
        self.type = cell_type
        self.state = 1
        self.death_period = -1

        self.wealth = 1
        self.pos = None

    def is_alive(self):

        if self.state == 1:
            return True
        return False

    def is_dead(self):
        if self.state == 0:
            return True
        return False

    def undergo_deterministic_death(self):

        self.age += 1
        if self.age == self.model.age_limit:
            self.state = 0

        if self.is_dead() and self.death_period == self.model.death_period_limit:
            self.model.new_cell2delete(self)

    def undergo_stochastic_death(self):

        self.age += 1
        if random.random() <= self.model.death_ratio:
            self.state = 0

        if self.is_dead() and self.death_period == self.model.death_period_limit:
            self.model.new_cell2delete(self)

    def crowded_neighborhood(self):

        neighbouring_cells = self.model.space.get_neighbors(self.pos, self.model.density_radius)
        for n in neighbouring_cells:
            if n.is_alive():
                print(n.unique_id, "is alive")
            else:
                print(n.unique_id, "is dead")

        def pow_2(x):
            return pow(x, 2)

        if len(neighbouring_cells) >= (pi * pow_2(self.model.density_radius) * self.model.max_cells_per_unit):
            return True

        return False

    def give_money(self):

        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            other = random.choice(cellmates)
            other.wealth += 1
            self.wealth -= 1

    def move(self, radius):

        possible_steps = self.model.space.get_neighbors(self.pos, radius=radius)

        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def step(self):

        if self.is_dead():
            self.death_period += 1
            print("Cell {} has death_period of {}".format(self.unique_id, self.death_period))
            return

        if self.model.deterministic_death:
            self.undergo_deterministic_death()
        else:
            self.undergo_stochastic_death()

        if self.is_dead():
            self.model.new_cell2delete(self)
            return'''

