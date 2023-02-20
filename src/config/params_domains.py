def generate_domain_dict(lower, upper):
    return {"l": lower, "u": upper}


ss = {
    "number_of_pivots": generate_domain_dict(lower=1, upper=100),
    "number_of_iterations": generate_domain_dict(lower=1, upper=200),
    "eps": generate_domain_dict(lower=0.01, upper=1),
}
