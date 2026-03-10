package com.burprest.routes

import com.burprest.models.AddScopeRequest
import com.burprest.models.ApiResponse
import com.burprest.models.SetScopeRequest
import com.burprest.services.TargetService
import io.ktor.server.application.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*

fun Route.targetRoutes(service: TargetService) {
    route("/target") {
        get("/sitemap") {
            val urlPrefix = call.parameters["url"]
            call.respond(ApiResponse.ok(service.getSitemap(urlPrefix)))
        }

        get("/scope") {
            call.respond(ApiResponse.ok(service.getScope()))
        }

        post("/scope") {
            val request = call.receive<SetScopeRequest>()
            call.respond(ApiResponse.ok(service.setScope(request)))
        }

        post("/scope/add") {
            val request = call.receive<AddScopeRequest>()
            call.respond(ApiResponse.ok(service.addToScope(request)))
        }

        post("/scope/remove") {
            val request = call.receive<AddScopeRequest>()
            call.respond(ApiResponse.ok(service.removeFromScope(request)))
        }

        get("/scope/check") {
            val url = call.parameters["url"]
                ?: return@get call.respond(ApiResponse.error<Unit>("INVALID_PARAM", "Missing url"))
            call.respond(ApiResponse.ok(service.isInScope(url)))
        }
    }
}
