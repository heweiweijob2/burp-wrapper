package com.burprest.routes

import com.burprest.models.ApiResponse
import com.burprest.models.BatchSendRequest
import com.burprest.models.CreateTabRequest
import com.burprest.models.SendRequest
import com.burprest.services.RepeaterService
import io.ktor.server.application.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*

fun Route.repeaterRoutes(service: RepeaterService) {
    route("/repeater") {
        post("/send") {
            val request = call.receive<SendRequest>()
            call.respond(ApiResponse.ok(service.send(request)))
        }

        post("/send/batch") {
            val request = call.receive<BatchSendRequest>()
            call.respond(ApiResponse.ok(service.sendBatch(request)))
        }

        post("/tab/create") {
            val request = call.receive<CreateTabRequest>()
            call.respond(ApiResponse.ok(service.createTab(request)))
        }
    }
}
