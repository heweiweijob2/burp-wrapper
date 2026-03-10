package com.burprest.services

import burp.api.montoya.MontoyaApi
import com.burprest.models.*
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap

class IntruderService(private val api: MontoyaApi, private val repeaterService: RepeaterService) {

    private val attacks = ConcurrentHashMap<String, AttackState>()

    data class AttackState(
        val id: String,
        var status: String = "created",
        var progress: Int = 0,
        var requestCount: Int = 0,
        var errorCount: Int = 0,
        val results: MutableList<AttackResultEntry> = mutableListOf(),
    )

    fun createAttack(request: CreateAttackRequest): CreateAttackResponse {
        val id = UUID.randomUUID().toString().take(8)
        attacks[id] = AttackState(id = id)
        return CreateAttackResponse(attackId = id, status = "created")
    }

    fun startAttack(id: String): AttackStatusResponse {
        val attack = attacks[id] ?: throw IllegalArgumentException("Attack not found: $id")
        attack.status = "running"
        return attackStatus(id)
    }

    fun attackStatus(id: String): AttackStatusResponse {
        val attack = attacks[id] ?: throw IllegalArgumentException("Attack not found: $id")
        return AttackStatusResponse(
            attackId = id,
            status = attack.status,
            progress = attack.progress,
            requestCount = attack.requestCount,
            errorCount = attack.errorCount,
        )
    }

    fun attackResults(id: String): AttackResultsResponse {
        val attack = attacks[id] ?: throw IllegalArgumentException("Attack not found: $id")
        return AttackResultsResponse(
            attackId = id,
            results = attack.results.toList(),
            total = attack.results.size,
        )
    }

    fun pauseAttack(id: String): AttackStatusResponse {
        val attack = attacks[id] ?: throw IllegalArgumentException("Attack not found: $id")
        attack.status = "paused"
        return attackStatus(id)
    }

    fun resumeAttack(id: String): AttackStatusResponse {
        val attack = attacks[id] ?: throw IllegalArgumentException("Attack not found: $id")
        attack.status = "running"
        return attackStatus(id)
    }

    fun stopAttack(id: String): AttackStatusResponse {
        val attack = attacks[id] ?: throw IllegalArgumentException("Attack not found: $id")
        attack.status = "stopped"
        return attackStatus(id)
    }

    fun quickFuzz(request: QuickFuzzRequest): QuickFuzzResponse {
        val results = mutableListOf<AttackResultEntry>()
        val start = System.currentTimeMillis()

        request.payloads.forEachIndexed { idx, payload ->
            try {
                val baseRequest = if (request.request != null) {
                    request.request
                } else if (request.requestId != null) {
                    val history = api.proxy().history()
                    require(request.requestId in history.indices)
                    val req = history[request.requestId].finalRequest()
                    HttpRequestData(
                        method = req.method(),
                        url = req.url(),
                        headers = req.headers().map { HttpHeader(it.name(), it.value()) },
                        body = if (req.body().length() > 0) req.bodyToString() else null,
                    )
                } else {
                    throw IllegalArgumentException("Either 'request' or 'requestId' required")
                }

                val modifiedUrl = baseRequest.url.replace("{${request.param}}", payload)
                    .replace(request.param + "=" + "[^&]*".toRegex().find(baseRequest.url.substringAfter(request.param + "="))?.value.orEmpty(),
                        request.param + "=" + payload)

                val modifiedBody = baseRequest.body?.replace("{${request.param}}", payload)

                val sendReq = SendRequest(
                    request = baseRequest.copy(url = modifiedUrl, body = modifiedBody),
                )

                val resp = repeaterService.send(sendReq)
                results.add(
                    AttackResultEntry(
                        index = idx,
                        payload = payload,
                        statusCode = resp.response.statusCode,
                        length = resp.response.body?.length ?: 0,
                        durationMs = resp.durationMs,
                    )
                )

                if (request.options.throttleMs > 0) {
                    Thread.sleep(request.options.throttleMs)
                }
            } catch (e: Exception) {
                results.add(
                    AttackResultEntry(
                        index = idx,
                        payload = payload,
                        statusCode = 0,
                        length = 0,
                        durationMs = 0,
                        error = e.message,
                    )
                )
            }
        }

        return QuickFuzzResponse(
            results = results,
            total = results.size,
            durationMs = System.currentTimeMillis() - start,
        )
    }
}
