
def handle_conf_file(top_gen_auto_mode_path):
    auto_mode_param_dict = {}
    with open(top_gen_auto_mode_path) as param_file:
        for line in param_file:
            (key, val) = line.split(":")
            auto_mode_param_dict[key] = val
    return auto_mode_param_dict

def create_auto_mode_param_file(top_gen_output_path):
    auto_mode_param_file_path = ""
    auto_mode_param_file_content = ""
    for element in top_gen_output_path:
        auto_mode_param_file_path += element + "/"
    auto_mode_param_file_path += "auto_mode_params"
    try:
        auto_mode_param_file = open(auto_mode_param_file_path, "r")
        for line in auto_mode_param_file:
            auto_mode_param_file_content += line
        auto_mode_param_file.close()
    except:
        pass
    auto_mode_param_file = open(auto_mode_param_file_path, "a")
    if auto_mode_param_file_content == "":
        auto_mode_param_file.write("Top module's filename: \nDescription comment: \nTop module's parameters: \n")
        auto_mode_param_file.write("Files to include: \nTop module's instantiation name: \n")
        print("Please fill up the auto-generated file.\n")
    else:
        print("Configuration file for automatic mode detected.\n")
        print("If the file is not up to date, please fix or delete it and restart the process.\n")
    auto_mode_param_file.close()
    input("Press enter!\n")
    return auto_mode_param_file_path

