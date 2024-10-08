# IMPORTS
from abc import ABC, abstractmethod
import itertools as iter

from schedule import Schedule
from paintshop import PaintShop


# CONSTANTS
PS = PaintShop()


# Move (Abstract Base Class) (https://docs.python.org/3/library/abc.html)
class Move(ABC):
    
    # As I'm still testing out abstract base classes, I'm raising an exception.
    # Apparantly, this method can only be called by subclasses calling super.func()
    @abstractmethod
    def get_moved(self, schedule_old: Schedule) -> Schedule:
        raise Exception("Abstract method used.")
    
    @staticmethod
    # @abstractmethod
    def get_moves(schedule: Schedule): # -> list[Move]
        
        return [
            *SwapMove.get_moves(schedule),
            *MoveMove.get_moves(schedule),
            *SwapQueuesMove.get_moves(schedule)
        ]
        # raise Exception("Abstract method used.")

    # @abstractmethod
    # def get_gain(self) -> float:
    #     raise Exception("Abstract method used.")

# Swap two orders by queue index.
class SwapMove(Move):
    
    # Constructor
    def __init__(self, queue_indices: tuple[tuple[int, int], tuple[int, int]]):
        self.a = queue_indices[0]
        self.b = queue_indices[1]
        
    # STR
    def __str__(self):
        return f'swap-items: {self.a} <=> {self.b}'
    
    # Returns a swapped copy of the specified schedule.
    def get_moved(self, old: Schedule) -> Schedule:
        
        # Create copy of schedule
        new = old.get_copy()
        
        # Apply swap to new
        new[self.b] = old[self.a]
        new[self.a] = old[self.b]
        
        # Return swapped copy
        return new
    
    @staticmethod
    def get_moves(schedule: Schedule):
        
        # Get all queue-indices of the orders.
        order_indices = [
            (machine_id, queue_index) 
            for machine_id in PS.machine_ids for queue_index in range(len(schedule[machine_id, :]))
        ]
        
        # Return all combinations of length 2.
        return [
            SwapMove(swap) for swap in list(iter.combinations(order_indices, 2))
        ]
    
    # # Get the change in cost resulting from this swap in a optimised way.
    # def get_gain(self, s: Schedule):
        
    #     return 

# Swap two orders by queue index.
class MoveMove(Move):
    
    def __init__(self, queue_indices: tuple[tuple[int, int], tuple[int, int]]):
        self.old_index = queue_indices[0]
        self.new_index = queue_indices[1]
    
    # STR
    def __str__(self):
        return f'move-item: {self.old_index} => {self.new_index}'
    
    # Returns a swapped copy of the specified schedule.
    def get_moved(self, old: Schedule) -> Schedule:
        
        # Create copy of schedule
        new = old.get_copy()
        
        # Apply move (little something i leared called 'slice assignment' and the 'del keyword')
        new[self.new_index[0], self.new_index[1]:self.new_index[1]] = [old[self.old_index]]
        del new[self.old_index]
        
        # Return swapped copy
        return new
    
    # Return all possible move-moves
    @staticmethod
    def get_moves(schedule: Schedule):
        
        # Get all queue-indices of the orders. [(0,0), (0,1), (0,2), ...]
        order_indices = [
            (machine_id, queue_index) 
            for machine_id in PS.machine_ids for queue_index in range(len(schedule[machine_id, :]))
        ]
        
        # Create list of all moves where item 1 is put in from of item 2 (this excludes cases where an item would be put in front of itself)
        moves = list(iter.combinations(order_indices, 2))
        
        # Add the moves where it is added to the end of a queue (slice assigment will add it to the end. It will not throw AOB)
        for order_index in order_indices:
            
            # If not last in queue
            if not schedule.is_last_in_queue(order_index):
                
                # Add move where it is added to the end of the queue
                moves += [
                    (
                        order_index, 
                        (machine_id, len(schedule[machine_id, :]))
                    )
                    for machine_id in PS.machine_ids
                ]
        
        # Remove moves where it would be inserted behind itself. (this would do nothing, since the source is deleted afterwards)
        moves = [
            move for move in moves if 
            (move[0][0] != move[1][0]) or          # Allow if not in same queue
            (not (move[0][1] == (move[1][1] - 1))) # But not if the target is behind the source
        ]
        
        # Return instances
        return [MoveMove(move) for move in moves]

    

# Swaps the queue of two machines.
class SwapQueuesMove(Move):
    
    def __init__(self, move: tuple[int, int]):
        self.machine_a = move[0]
        self.machine_b = move[1]
    
    
    # STR
    def __str__(self):
        return f'swap-queues: {self.machine_a} => {self.machine_b}'
    
    
    def get_moved(self, old: Schedule) -> Schedule:
        
        # Create copy of schedule
        new = old.get_copy()
        
        # Apply move (swap two queues)
        new[self.machine_a, :] = old[self.machine_b, :]
        new[self.machine_b, :] = old[self.machine_a, :]
        
        # Return swapped copy
        return new
    
    
    @staticmethod
    def get_moves(schedule: Schedule):
        
        # Return all 2-item combinations of the machine ID's
        return [SwapQueuesMove(move) for move in list(iter.combinations(PS.machine_ids, 2))]
    
    
# class ShuffleEach(Move):
    
#     def get_moved(self, schedule_old: Schedule) -> Schedule:
        
#         # Create copy of schedule
#         new = copy.deepcopy(schedule_old)
        
#         # Apply move (shuffle each queue)
#         new[self.new_index[0], self.new_index[1]:self.new_index[1]] = [schedule_old[self.old_index]]
#         del new[self.old_index]
        
#         # Return swapped copy
#         return new
        

# ???
Move.register(SwapMove)
Move.register(MoveMove)
Move.register(SwapQueuesMove)