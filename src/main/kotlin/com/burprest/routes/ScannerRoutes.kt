package com.burprest.routes

import com.burprest.models.ApiResponse
import com.burprest.models.ScanRequest
import com.burprest.services.ScannerService
import io.ktor.server.application.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*

fun Route.scannerRoutes(service: ScannerService) {
    route("/scanner") {
        post("/crawl") {
            val request = call.receive<ScanRequest>()
            call.respond(ApiResponse.ok(service.crawl(request)))
        }

        post("/audit") {
            val request = call.receive<ScanRequest>()
            call.respond(ApiResponse.ok(service.audit(request)))
        }

        post("/crawl-and-audit") {
            val request = call.receive<ScanRequest>()
            call.respond(ApiResponse.ok(service.crawlAndAudit(request)))
        }

        get("/{id}/status") {
            val id = call.parameters["id"]!!
            call.respond(ApiResponse.ok(service.status(id)))
        }

        get("/{id}/issues") {
            val id = call.parameters["id"]!!
            call.respond(ApiResponse.ok(service.issues(id)))
        }

        post("/{id}/pause") {
            val id = call.parameters["id"]!!
            call.respond(ApiResponse.ok(service.pause(id)))
        }

        post("/{id}/resume") {
            val id = call.parameters["id"]!!
            call.respond(ApiResponse.ok(service.resume(id)))
        }

        post("/{id}/stop") {
            val id = call.parameters["id"]!!
            call.respond(ApiResponse.ok(service.stop(id)))
        }

        get("/issue-definitions") {
            call.respond(ApiResponse.ok(service.issueDefinitions()))
        }
    }
}
