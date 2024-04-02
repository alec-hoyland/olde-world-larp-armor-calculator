import yaml
import scipy.optimize as optimize
from pprint import pprint
import numpy as np
import pydantic
from typing import List, Dict, Tuple
import argparse


class Resource(pydantic.BaseModel):
    """Resource class to represent a resource in the game"""

    name: str
    count: int


class Ingredient(pydantic.BaseModel):
    """Ingredient class to represent an ingredient in a recipe"""

    name: str
    count: int


class Recipe(pydantic.BaseModel):
    """Recipe class to represent a recipe in the game"""

    name: str
    priority: int
    ingredients: list[Ingredient]


class Program(pydantic.BaseModel):
    """Program class to represent the linear program"""

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)
    A_ub: np.ndarray
    b_ub: np.ndarray
    c: np.ndarray
    resources: List[Resource]
    recipes: List[Recipe]


def read_resources_file(file_path: str) -> List[Resource]:
    with open(file_path, "r") as file:
        resources = yaml.safe_load(file)
    return [Resource(name=k, count=v) for k, v in resources.items()]


def read_recipes_file(file_path: str) -> List[Recipe]:
    output = []
    with open(file_path, "r") as file:
        recipes = yaml.safe_load(file)
    for recipe_name, recipe in recipes.items():
        if isinstance(recipe["ingredients"], list):
            # recipe has multiple paths, handle each individually
            for ingredient_dict in recipe["ingredients"]:
                output.append(
                    Recipe(
                        name=recipe_name,
                        priority=recipe["priority"],
                        ingredients=[
                            Ingredient(name=k, count=v)
                            for k, v in ingredient_dict.items()
                        ],
                    )
                )
        else:
            output.append(
                Recipe(
                    name=recipe_name,
                    priority=recipe["priority"],
                    ingredients=[
                        Ingredient(name=k, count=v)
                        for k, v in recipe["ingredients"].items()
                    ],
                )
            )

    return output


def setup_program(resources: List[Resource], recipes: List[Recipe]) -> Program:
    resource_names = [resource.name for resource in resources]
    b_ub = np.array([resource.count for resource in resources])
    c = -np.array([recipe.priority for recipe in recipes])

    A_ub = np.zeros((len(resources), len(recipes)))
    for j, recipe in enumerate(recipes):
        for ingredient in recipe.ingredients:
            i = resource_names.index(ingredient.name)
            A_ub[i][j] = ingredient.count

    return Program(A_ub=A_ub, b_ub=b_ub, c=c, resources=resources, recipes=recipes)


def summarize(
    program: Program, res: optimize.OptimizeResult
) -> Tuple[Dict[str, int], Dict[str, int]]:
    resource_counter: Dict[str, int] = {}
    recipe_counter: Dict[str, int] = {}
    for i, recipe in enumerate(program.recipes):
        count = int(res.x[i])
        if count > 0:
            for ingredient in recipe.ingredients:
                if ingredient.name in resource_counter.keys():
                    resource_counter[ingredient.name] += ingredient.count * count
                else:
                    resource_counter[ingredient.name] = ingredient.count * count
            if recipe.name in recipe_counter.keys():
                recipe_counter[recipe.name] += count
            else:
                recipe_counter[recipe.name] = count
    return resource_counter, recipe_counter


def display_results(resource_counter: Dict[str, int], recipe_counter: Dict[str, int]):
    print("You can craft the following:")
    print("-----------------------------")
    pprint(recipe_counter)
    print("-----------------------------")
    print("It will cost you:")
    print("-----------------------------")
    pprint(resource_counter)


def parse_args():
    parser = argparse.ArgumentParser(description="Resource Utilizer")
    parser.add_argument(
        "--resources",
        type=str,
        default="resources.yaml",
        help="Path to the resources file",
    )
    parser.add_argument(
        "--recipes", type=str, default="recipes.yaml", help="Path to the recipes file"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    resources = read_resources_file(args.resources)
    recipes = read_recipes_file(args.recipes)
    program = setup_program(resources, recipes)
    res = optimize.linprog(
        c=program.c, A_ub=program.A_ub, b_ub=program.b_ub, method="highs", integrality=1
    )
    resource_counter, recipe_counter = summarize(program, res)
    display_results(resource_counter, recipe_counter)
