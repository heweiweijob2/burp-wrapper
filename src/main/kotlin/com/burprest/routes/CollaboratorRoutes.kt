package com.burprest.routes

import com.burprest.models.ApiResponse
import com.burprest.models.BatchGenerateRequest
import com.burprest.services.CollaboratorService
import io.ktor.server.application.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*

fun Route.collaboratorRoutes(service: CollaboratorService) {
    route("/collaborator") {
        post("/generate") {
            call.respond(ApiResponse.ok(service.generatePayload()))
        }

        post("/generate/batch") {
            val request = call.receive<BatchGenerateRequest>()
            call.respond(ApiResponse.ok(service.generateBatch(request.count)))
        }

        get("/poll") {
            call.respond(ApiResponse.ok(service.poll()))
        }

        get("/poll/{id}") {
            val id = call.parameters["id"]
                ?: return@get call.respond(ApiResponse.error<Unit>("INVALID_PARAM", "Missing ID"))
            call.respond(ApiResponse.ok(service.pollById(id)))
        }
    }
}
