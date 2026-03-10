package com.burprest.services

import burp.api.montoya.MontoyaApi
import com.burprest.models.*

class ConfigService(private val api: MontoyaApi) {

    fun getProjectConfig(): ConfigResponse {
        return ConfigResponse(config = mapOf("type" to "project"))
    }

    fun updateProjectConfig(request: ConfigUpdateRequest): ConfigResponse {
        return ConfigResponse(config = request.config)
    }

    fun getUserConfig(): ConfigResponse {
        return ConfigResponse(config = mapOf("type" to "user"))
    }

    fun updateUserConfig(request: ConfigUpdateRequest): ConfigResponse {
        return ConfigResponse(config = request.config)
    }

    fun getExtensions(): ExtensionsListResponse {
        // Montoya API only exposes the current extension via extension() (singular)
        // Cannot list all extensions — return info about this extension only
        val ext = api.extension()
        return ExtensionsListResponse(
            extensions = listOf(
                ExtensionInfo(
                    name = "Burp REST API",
                    enabled = true,
                    filename = ext.filename(),
                )
            ),
            total = 1,
        )
    }
}
