package com.burprest.routes

import com.burprest.models.ApiResponse
import com.burprest.models.ConfigUpdateRequest
import com.burprest.services.ConfigService
import io.ktor.server.application.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*

fun Route.configRoutes(service: ConfigService) {
    route("/config") {
        get("/project") {
            call.respond(ApiResponse.ok(service.getProjectConfig()))
        }

        put("/project") {
            val request = call.receive<ConfigUpdateRequest>()
            call.respond(ApiResponse.ok(service.updateProjectConfig(request)))
        }

        get("/user") {
            call.respond(ApiResponse.ok(service.getUserConfig()))
        }

        put("/user") {
            val request = call.receive<ConfigUpdateRequest>()
            call.respond(ApiResponse.ok(service.updateUserConfig(request)))
        }
    }

    get("/extensions") {
        call.respond(ApiResponse.ok(service.getExtensions()))
    }
}
