package com.burprest.routes

import com.burprest.models.ApiResponse
import com.burprest.models.HealthResponse
import com.burprest.models.VersionResponse
import io.ktor.server.application.*
import io.ktor.server.response.*
import io.ktor.server.routing.*

fun Route.healthRoutes(startTime: Long) {
    get("/health") {
        val uptime = (System.currentTimeMillis() - startTime) / 1000
        call.respond(
            ApiResponse.ok(
                HealthResponse(
                    status = "ok",
                    version = "0.1.0",
                    uptime = uptime,
                )
            )
        )
    }

    get("/version") {
        call.respond(
            ApiResponse.ok(
                VersionResponse(
                    version = "0.1.0",
                    name = "burp-rest-extension",
                )
            )
        )
    }

    get("/docs") {
        call.respondText(OPENAPI_STUB, io.ktor.http.ContentType.Application.Json)
    }
}

private val OPENAPI_STUB = """
{
  "openapi": "3.0.3",
  "info": {
    "title": "Burp REST Extension API",
    "version": "0.1.0",
    "description": "REST API exposing Burp Suite Montoya API"
  },
  "servers": [{"url": "http://127.0.0.1:8089"}],
  "paths": {
    "/health": {"get": {"summary": "Health check", "responses": {"200": {"description": "OK"}}}},
    "/proxy/history": {"get": {"summary": "Proxy history"}},
    "/repeater/send": {"post": {"summary": "Send request"}},
    "/collaborator/generate": {"post": {"summary": "Generate collaborator payload"}},
    "/intruder/quick-fuzz": {"post": {"summary": "Quick fuzz a parameter"}},
    "/scanner/crawl-and-audit": {"post": {"summary": "Start crawl and audit"}},
    "/target/sitemap": {"get": {"summary": "Get sitemap"}},
    "/decoder/encode": {"post": {"summary": "Encode data"}},
    "/decoder/decode": {"post": {"summary": "Decode data"}}
  }
}
""".trimIndent()
