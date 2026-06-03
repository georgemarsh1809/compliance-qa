import type { QueryRequest, QueryResponse } from './types';

export async function queryCompliance(
    question: string,
): Promise<QueryResponse> {
    const queryRequest: QueryRequest = {
        question: question,
    };

    const url: string = 'http://localhost:8000/query';

    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(queryRequest),
    });

    return response.json() as Promise<QueryResponse>;
}
