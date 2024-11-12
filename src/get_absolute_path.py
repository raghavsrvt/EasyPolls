import os
def resource_path(relative_path:str):
    """ Get absolute path to resource."""
    try:
        base_path = os.path.abspath(".")
    except:
        print('Some error occured while retrieving resource path')        
 
    return os.path.join(base_path, relative_path)