package com.burprest.services

import burp.api.montoya.MontoyaApi
import com.burprest.models.*

class TargetService(private val api: MontoyaApi) {

    fun getSitemap(urlPrefix: String? = null): SitemapResponse {
        val entries = if (urlPrefix != null) {
            api.siteMap().requestResponses(burp.api.montoya.sitemap.SiteMapFilter.prefixFilter(urlPrefix))
        } else {
            api.siteMap().requestResponses()
        }

        return SitemapResponse(
            entries = entries.map {
                SitemapEntry(
                    url = it.request().url(),
                    method = it.request().method(),
                    statusCode = it.response()?.statusCode()?.toInt(),
                    mimeType = it.response()?.statedMimeType()?.name,
                )
            },
            total = entries.size,
        )
    }

    fun getScope(): ScopeResponse {
        // Montoya API doesn't expose scope listing — return empty
        return ScopeResponse(includes = emptyList(), excludes = emptyList())
    }

    fun setScope(request: SetScopeRequest): ScopeResponse {
        request.includes.forEach { url ->
            api.scope().includeInScope(url)
        }
        request.excludes.forEach { url ->
            api.scope().excludeFromScope(url)
        }
        return ScopeResponse(includes = request.includes, excludes = request.excludes)
    }

    fun addToScope(request: AddScopeRequest): ScopeCheckResponse {
        api.scope().includeInScope(request.url)
        return ScopeCheckResponse(url = request.url, inScope = true)
    }

    fun removeFromScope(request: AddScopeRequest): ScopeCheckResponse {
        api.scope().excludeFromScope(request.url)
        return ScopeCheckResponse(url = request.url, inScope = false)
    }

    fun isInScope(url: String): ScopeCheckResponse {
        val inScope = api.scope().isInScope(url)
        return ScopeCheckResponse(url = url, inScope = inScope)
    }
}
