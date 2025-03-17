################################################################################################
# This script is used to parse a YAML file containing a CV and convert it into a LaTeX file.   #
################################################################################################

DICTIONARY = {
    "address": {
        "en": "Address",
        "de": "Adresse",
        "fr": "Adresse"
    },
    "phone": {
        "en": "Phone",
        "de": "Telefon",
        "fr": "Téléphone"
    },
    "no end": {
        "en": "Present",
        "de": "Heute",
        "fr": "Maintenant"
    }
}


import yaml
import os
import datetime


def main():
    with open('inputs/cv.yaml', 'r') as file:
        data = yaml.safe_load(file)
    cv_header, cv_left, cv_right = parse_cv_data(data, 'en')
    generate_pdf('templates/cv_template.tex', 'outputs', 'en', cv_header, cv_right, cv_left)
    cv_header, cv_left, cv_right = parse_cv_data(data, 'de')
    generate_pdf('templates/cv_template.tex', 'outputs', 'de', cv_header, cv_right, cv_left)
    cv_header, cv_left, cv_right = parse_cv_data(data, 'fr')
    generate_pdf('templates/cv_template.tex', 'outputs', 'fr', cv_header, cv_right, cv_left)

def generate_pdf(template, output_folder, language, tex_header, tex_right, tex_left):
    with open(template, 'r') as file:
        template = file.read()
    template = template.replace('##HEADER##', tex_header)
    template = template.replace('##RIGHT##', tex_right)
    template = template.replace('##LEFT##', tex_left)
    date = datetime.datetime.now().strftime("%Y_%m_%d")
    #Check if the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    output_file = f"{output_folder}/{date}_CV_{language}.tex"
    with open(output_file, 'w') as file:
        file.write(template)
    os.system(f'xelatex -output-directory={output_folder}/ -interaction=nonstopmode {output_file}')
    os.system(f'xelatex -output-directory={output_folder}/ -interaction=nonstopmode {output_file}')
    #Remove the auxillary files
    os.system(f'rm {output_folder}/*.aux')
    os.system(f'rm {output_folder}/*.log')
    os.system(f'rm {output_folder}/*.out')

def parse_cv_data(data, language):
    tex_header, tex_left, tex_right = '', '', ''
    try:
        data = data['cv']
    except KeyError:
        raise ValueError('The CV data must contain a "cv" key')
    keys = data.keys()
    for key in keys:
        match key:
            case 'styling':
                header, left, right = parse_styling(data[key], language)
            case 'personal information':
                header, left, right = parse_personal_info(data[key], language)
            case 'education':
                header, left, right = parse_education(data[key], language)
            case 'work experience':
                header, left, right = parse_work_experience(data[key], language)
            case 'languages':
                header, left, right = parse_languages(data[key], language)    
            case 'programming':
                header, left, right = parse_programming(data[key], language)
            case 'volonteering':
                header, left, right = parse_volonteering(data[key], language)
            case _:
                raise ValueError(f'Invalid key: {key}')
        tex_header += header
        tex_left += left
        tex_right += right

    return tex_header, tex_left, tex_right

def parse_styling(data, language):
    tex_header, tex_left, tex_right = '', '', ''
    if "main color" in data:
        color = data['main color']
        if color.startswith('#'):
            color = color[1:]
        tex_header += f"\\definecolor{{MainColor}}{{HTML}}{{{color}}}\n"
    if "accent color" in data:
        color = data['accent color']
        if color.startswith('#'):
            color = color[1:]
        tex_header += f"\\definecolor{{AccentColor}}{{HTML}}{{{color}}}\n"
    if "font size" in data:
        tex_header += f"\\renewcommand{{\\normalsize}}{{\\fontsize{{{data['font size']}}}{{12pt}}\\selectfont}}\n"
    if "font family" in data:
        tex_header += f"\\renewcommand{{\\familydefault}}{{\\sfdefault}}\n"
    return tex_header, tex_left, tex_right

def parse_personal_info(data, language):
    tex_header, tex_left, tex_right = '', '', ''
    if data['type'] != "personal information":
        raise ValueError('The type of personal information must be "personal information"')
    try:
        entries = data['entries']
    except KeyError:
        raise ValueError('The personal information must contain an "entries" key')
    #Check if there is a picture
    if 'picture' in entries:
        tex_left += f"\\includegraphics[width=0.6\\columnwidth]{{{entries["picture"]}}}\\\\[\\baselineskip]\n"
    try:
        tex_left += f"{entries['name']}\\\\ \n"
    except KeyError:
        raise ValueError('The personal information must contain a "name" key')
    if 'email' in entries:
        tex_left += f"\\url{{{entries['email']}}}\\\\ \n"
    if 'phone' in entries:
        tex_left += f"{entries['phone']}\\\\ \n"
    if 'address' in entries:
        tex_left += "\\Sep\n"
        try:
            tex_left += f"\\textbf{{{DICTIONARY["address"][language]}}}\\\\ \n{entries['address']['street']} \\\\ \n{entries['address']['city']} {entries['address']['postal code']} \\\\\n"
        except KeyError:
            raise ValueError('The address must contain a "street", "city", and "postal code" key')
        if 'country' in entries['address']:
            try:
                tex_left += f"{entries['address']['country'][language]} \\\\ \n"
            except KeyError:    
                raise ValueError(f'The country must contain an "{language}" key')

    return tex_header, tex_left, tex_right


def parse_education(data, language):
    tex_header, tex_left, tex_right = '', '', ''
    if data['type'] != "section":
        raise ValueError('The type of education must be "section"')
    try:
        entries = data['entries']
    except KeyError:
        raise ValueError('The education must contain an "entries" key')
    try:
        tex_right += f"\\CVSection{{{data['name'][language]}}}\n"
    except KeyError:
        raise ValueError(f'The education must contain a "name" key, in the language {language}')
    for entry in entries:
        try:
            start = entry['start']
            end = entry['end']
            if end is None:
                end = DICTIONARY["no end"][language]
            tex_right += f"\\CVItem{{{start} - {end}, {entry['school']}}}{{{entry['degree'][language]}}}\n \n"
        except KeyError:
            raise ValueError('The education entry must contain a "start", "end", "school", and "degree" key')
        
    tex_right += "\\Sep\n"
    return tex_header, tex_left, tex_right

def parse_work_experience(data, language):
    tex_header, tex_left, tex_right = '', '', ''
    if data['type'] != "section":
        raise ValueError('The type of work experience must be "section"')
    try:
        entries = data['entries']
    except KeyError:
        raise ValueError('The work experience must contain an "entries" key')
    try:
        tex_right += f"\\CVSection{{{data['name'][language]}}}\n"
    except KeyError:
        raise ValueError(f'The work experience must contain a "name" key, in the language {language}')
    for entry in entries:
        try:
            start = entry['start']
            end = entry['end']
            if end is None:
                end = DICTIONARY["no end"][language]
            tex_right += f"\\CVItem{{{start} - {end}, \\textit{{{entry['position'][language]}}}, {entry['company']}}}{{\n"
        except KeyError:
            raise ValueError('The work experience entry must contain a "start", "end", "company", and "position" key')
        try:
            #Split the description into itemized list if it is a list
            if isinstance(entry['description'][language], list):
                tex_right += "\\begin{itemize}\n"
                for item in entry['description'][language]:
                    tex_right += f"\\item {item}\n"
                tex_right += "\\end{itemize}\n"
            else:
                tex_right += f"{entry['description'][language]}\n"
        except KeyError:
            raise ValueError('The work experience entry must contain a "description" key')
        tex_right += "}\n\n"
    tex_right += "\\Sep\n"
    return tex_header, tex_left, tex_right

def parse_languages(data, language):
    tex_header, tex_left, tex_right = '', '', ''
    if data['type'] != "leftcolumn":
        raise ValueError('The type of languages must be "leftcolumn"')
    try:
        entries = data['entries']
    except KeyError:
        raise ValueError('The languages must contain an "entries" key')
    tex_left += "\\Sep\n"
    tex_left += f"\\textbf{{{data['name'][language]}}}\\\\ \n"
    for entry in entries:
        try:
            tex_left += f"{entry['language'][language]} ({entry['proficiency'][language]})\\\\ \n"
        except KeyError:
            raise ValueError('The language entry must contain a "name" and "proficiency" key')
    return tex_header, tex_left, tex_right

def parse_programming(data, language):
    tex_header, tex_left, tex_right = '', '', ''
    if data['type'] != "leftcolumn":
        raise ValueError('The type of programming must be "leftcolumn"')
    try:
        entries = data['entries']
    except KeyError:
        raise ValueError('The programming must contain an "entries" key')
    tex_left += "\\Sep\n"
    tex_left += f"\\textbf{{{data['name'][language]}}}\\\\ \n"
    for entry in entries:
        try:
            tex_left += f"{entry['language']} \\\\ \n"
        except KeyError:
            raise ValueError('The programming entry must contain a "name" key')
    return tex_header, tex_left, tex_right

def parse_volonteering(data, language):
    tex_header, tex_left, tex_right = '', '', ''
    if data['type'] != "section":
        raise ValueError('The type of volonteering must be "section"')
    try:
        entries = data['entries']
    except KeyError:
        raise ValueError('The volonteering must contain an "entries" key')
    try:
        tex_right += f"\\CVSection{{{data['name'][language]}}}\n"
    except KeyError:
        raise ValueError(f'The volonteering must contain a "name" key, in the language {language}')
    for entry in entries:
        try:
            start = entry['start']
            end = entry['end']
            if end is None:
                end = DICTIONARY["no end"][language]
            tex_right += f"\\CVItem{{{start} - {end}, {entry['organization']}}}{{{entry['position'][language]}}}\n \n"
        except KeyError:
            raise ValueError('The volonteering entry must contain a "start", "end", "organization", and "position" key')
    tex_right += "\\Sep\n"
    return tex_header, tex_left, tex_right

if __name__ == '__main__':
    main()