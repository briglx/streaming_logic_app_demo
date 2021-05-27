"""Template with jinja2 engine."""
import json

from jinja2 import Environment, FileSystemLoader


def load_data(filename):
    """Load source file."""
    with open(filename, "r") as myfile:
        text = myfile.read()
    data = json.loads(text)
    return data


def save_data(data, filename):
    """Save data to json file."""
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=2, separators=(",", ": "))


def render(data, template_path, template_name, filters=None):
    """Render data as a string for a given template."""
    # Load Environment
    loader = FileSystemLoader(template_path)
    env = Environment(loader=loader)

    # Register Filter
    if filters:
        for filter_name, filter_code in filters.items():
            env.filters[filter_name] = filter_code

    # env.filters["convert"] = mock_filter

    # Get Template
    template = env.get_template(template_name)

    # Transform
    result_string = template.render(data)

    return result_string


def render_dict(data, template_path, template_name, filters=None):
    """Render data as Json Dictionary for a given template."""
    result_string = render(data, template_path, template_name, filters)

    return json.loads(result_string)


def render_json(data, template_path, template_name, filters=None):
    """Render data as Json for a given template."""
    result_dict = render_dict(data, template_path, template_name, filters)
    return json.dumps(result_dict)
