# an index of filepaths stored within the Data folder, to group pathing information for easier refactoring
from pathlib import Path

DATA_PATH = Path(__file__).parent

PROPHECY_INFO = DATA_PATH.joinpath('CSV/ProphecyRecipes.csv')