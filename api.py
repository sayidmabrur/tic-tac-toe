def check_win_conditions(p1_trajectory, p2_trajectory):
        win_conditions = [
            # rows
            {(0, 0), (0, 1), (0, 2)},
            {(1, 0), (1, 1), (1, 2)},
            {(2, 0), (2, 1), (2, 2)},
            # columns
            {(0, 0), (1, 0), (2, 0)},
            {(0, 1), (1, 1), (2, 1)},
            {(0, 2), (1, 2), (2, 2)},
            # diagonals
            {(0, 0), (1, 1), (2, 2)},
            {(0, 2), (1, 1), (2, 0)},
        ]

        for condition in win_conditions:
            if condition.issubset(p1_trajectory):
                return True, 1
            elif condition.issubset(p2_trajectory):
                return True, 2
        return False, 0 #0 means game draw

