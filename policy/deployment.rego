package main

# Verifica que los deployments usen envFrom o valueFrom
deny contains msg if {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    
    # Verifica si hay variables de entorno definidas
    count(container.env) > 0
    
    # Verifica si se usa envFrom
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
    
    msg := sprintf("Deployment '%s' tiene la variable '%s' con valor hardcodeado en el contenedor '%s'", [input.metadata.name, env_var.name, container.name])
}