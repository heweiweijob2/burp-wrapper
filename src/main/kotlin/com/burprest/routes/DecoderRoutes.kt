package com.burprest.routes

import com.burprest.models.*
import com.burprest.services.DecoderService
import io.ktor.server.application.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*

fun Route.decoderRoutes(service: DecoderService) {
    route("/decoder") {
        post("/encode") {
            val request = call.receive<EncodeRequest>()
            call.respond(ApiResponse.ok(service.encode(request)))
        }

        post("/decode") {
            val request = call.receive<DecodeRequest>()
            call.respond(ApiResponse.ok(service.decode(request)))
        }

        post("/hash") {
            val request = call.receive<HashRequest>()
            call.respond(ApiResponse.ok(service.hash(request)))
        }

        post("/smart-decode") {
            val request = call.receive<DecodeRequest>()
            call.respond(ApiResponse.ok(service.smartDecode(request.data)))
        }
    }
}
