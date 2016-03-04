import os
import json
import click
import shutil
import config
import logging
from city import City
from world import social
from people import Person
from time import time
from datetime import timedelta


@click.command()
@click.argument('population', 'number of simulated citizens', type=int)
@click.argument('days', '(simulated) days to run', type=int)
@click.argument('arbiter', default=[])
def run(population, days, arbiter):
    run_simulation(population, days, arbiter)


def run_simulation(population, days, arbiter):
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('models.bnet').setLevel(logging.ERROR)

    if arbiter:
        host, port = arbiter.split(':')
        arbiter = (host, int(port))
    else:
        arbiter = None

    pop = generate_population(population)
    model = City(pop, arbiter=arbiter)

    s = time()
    with click.progressbar(range(days), label='simulating...') as days:
        for day in days:
            model.step()
    print('elapsed:', str(timedelta(seconds=time() - s)))

    print('gathering histories...')
    shutil.rmtree('histories')
    os.makedirs('histories')
    histories = model.history()
    for id, name, history, goals in histories:
        with open('histories/{}_{}.json'.format(name, id), 'w') as f:
            json.dump({
                'id': id,
                'name': name,
                'history': history,
                'goals': [goal.name for goal in goals]
            }, f)


def generate_population(n):
    population = []

    with click.progressbar(range(n), label='populating...') as n:
        for i in n:
            agent = Person.generate(config.START_DATE.year)
            population.append(agent)
            # print(agent, 'is moving into', agent.neighborhood)
            # print('  ', ','.join([agent.occupation, str(agent.sex), str(agent.race), agent.neighborhood, str(agent.education), str(agent.rent)]))

    social_network = social.social_network(population, base_prob=0.4)
    for i, person in enumerate(population):
        person.friends = [population[j] for _, j in social_network.edges(i)]
    return population


if __name__ == '__main__':
    run()