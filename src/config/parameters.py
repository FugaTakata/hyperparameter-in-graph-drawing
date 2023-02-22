def generate_domain_dict(lower, upper):
    return {"l": lower, "u": upper}


domain_ss = {
    "number_of_pivots": generate_domain_dict(lower=1, upper=100),
    "number_of_iterations": generate_domain_dict(lower=1, upper=200),
    "eps": generate_domain_dict(lower=0.01, upper=1),
}

empirical_ss = {
    "number_of_pivots": 50,
    "number_of_iterations": 100,
    "eps": 0.1,
}
