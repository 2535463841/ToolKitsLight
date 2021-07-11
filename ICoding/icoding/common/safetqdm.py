"""
Module tqdm wrapper
Prevent throwing exceptions due to import failure 
"""

# TODO
class SafeTqdm(object):

    def __init__(self) -> None:
        super().__init__()
