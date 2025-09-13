from langchain_core.prompts import PromptTemplate

prompt1 = PromptTemplate(
    template = """
Please provide me the information about {player_name}, where mainly focus on the player's {style_input} and can you please generate the content in this {length_input} size.
here make sure of the couple of things:
1. Provide a consise information about the player, if there is a need of mathematical reprensation show it.
2. Make the information as factual, accurate as possible and try not to imagine anything if don't know somethings just say so.
""",
input_variables=['player_name', 'style_input', 'length_input'],
validate_template=True)

prompt1.save('template.json')