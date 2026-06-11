import type { QueryRequest, QueryResponse } from './types';

const BASE_URL = import.meta.env.VITE_API_URL;

export async function queryCompliance(
    question: string,
): Promise<QueryResponse> {
    const queryRequest: QueryRequest = {
        question: question,
    };

    const response = await fetch(`${BASE_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(queryRequest),
    });

    return response.json() as Promise<QueryResponse>;
}
