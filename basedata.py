import utils


def extract_key_val_for_line(line):
    if ':' in line:
        parts = line.split(':')
        if '&' in parts[1]:
            keyname = parts[0].strip()
            valstr = parts[1].split('&')[0].strip()
            return keyname, valstr
    return None, None


def read_parameters_from_basefile(in_basefile_fn, parameter_names):
    lines = utils.slurp_lines(in_basefile_fn)
    odict = {}

    for line in lines:
        keyname, valstr = extract_key_val_for_line(line)
        if keyname in parameter_names:
            odict[keyname] = valstr

    return odict


def overwrite_parameters_in_basefile(in_basefile_fn, out_basefile_fn, mapping):
    orig_lines = utils.slurp_lines(in_basefile_fn)
    mod_lines = []

    for line in orig_lines:
        mod_line = line
        keyname, valstr = extract_key_val_for_line(line)
        if keyname in mapping:
            mod_line = line.replace(valstr, mapping[keyname])
        mod_lines.append(mod_line)

    utils.spit(''.join(mod_lines), out_basefile_fn)
