import time


def run_sensor(name:str, index:int, directions:list):
    """_summary_
    takes in the sensor name string and the index that the dirction the sensor reads in. The direction index
    is insipired from the directions list. The funtion takes this information, reads from the sensor and 
    stores the value in the directions list.
    Args:
        name (str): _description_
        name of the sensor
        index (int): _description_
        the index of the direction this sensor reads in. The direction is inspired from the directions list. 
        val (int):
        value of sensor
    Returns:
        _type_: _description_
        returns updated directions list
    """
    # print("SENSNNSONONRONONONONCHECKKCKCKCK")
    transmit(name)
    time.sleep(0.1)
    directions[index] = round(responses[0])
    # print(responses[0])
    return directions



def update_directions(directions:list):
    """
    Args:
        directions (list): _description_
    """
    directions = run_sensor('u0', 0, directions)
    time.sleep(0.1)
    directions = run_sensor('u1', 3, directions)
    time.sleep(0.1)
    directions = run_sensor('u2', 1, directions)
    time.sleep(0.1)
    directions = run_sensor('u3', 2, directions)
    time.sleep(0.1)
    directions = run_sensor('u4', 4, directions)
    time.sleep(0.1)
    directions = run_sensor('u5', 5, directions)
    time.sleep(0.1)
    directions = run_sensor('u6', 6, directions)
    time.sleep(0.1)
    directions = run_sensor('u7', 7, directions)
    time.sleep(0.1)
    print_text(directions)
    
    return directions


while True:
    