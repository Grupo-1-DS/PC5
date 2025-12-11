package main

# Patrones que indican posibles secretos hardcodeados
sensitive_patterns := [
    "password",
    "passwd",
    "secret",
    "key",
    "token",
    "api_key",
    "apikey",
    "credential",
]

# Verifica que los deployments usen envFrom o valueFrom
deny contains msg if {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    
    # Verifica si hay variables de entorno definidas
    count(container.env) > 0
    
    # Verifica que no haya envFrom ni valueFrom
    not container.envFrom
    
    # Verifica que ninguna variable use valueFrom
    env_var := container.env[_]
    not env_var.valueFrom
    
    msg := sprintf("Deployment '%s' contiene variables de entorno sin usar envFrom o valueFrom en el contenedor '%s'", [input.metadata.name, container.name])
}

# Detecta valores hardcodeados que parecen sensibles
deny contains msg if {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    env_var := container.env[_]
    
    # Si tiene un valor directo (no valueFrom)
    env_var.value
    not env_var.valueFrom
    
    # Verifica si el nombre o valor contiene patrones sensibles
    pattern := sensitive_patterns[_]
    contains(lower(env_var.name), pattern)
    
    msg := sprintf("Deployment '%s' tiene la variable '%s' con valor hardcodeado en el contenedor '%s'. Debe usar valueFrom para secrets", [input.metadata.name, env_var.name, container.name])
}