import { useState } from 'react';
import type { QueryResponse } from './types';
import { queryCompliance } from './api';
import { QueryForm } from './components/QueryForm';
import { ResponseDisplay } from './components/ResponseDisplay';

function App() {
    const [question, setQuestion] = useState('');
    const [response, setResponse] = useState<QueryResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    async function handleSubmit(question: string) {
        setIsLoading(true);
        const response = await queryCompliance(question);
        setResponse(response);
        setIsLoading(false);
    }

    return (
        <>
            <div className="min-h-screen bg-slate-900 flex flex-col">
                <header className="w-full px-6 py-4 border-b border-slate-700">
                    <h1 className="text-white italic ">ComplianceQA</h1>
                </header>
                <div className="flex flex-col max-w-3xl gap-6 w-full mx-auto px-6 py-12">
                    <p className="text-white">
                        ComplianceQA is a retrieval-augmented question answering
                        system built over the Food Safety Act 1990. Ask a
                        question about UK food safety law and it will return a
                        grounded answer with citations to the source document.
                    </p>
                    <a
                        href="https://www.food.gov.uk/sites/default/files/media/document/Food%20standards%20safety%20act%201990%20PDF.pdf"
                        target="_blank"
                        className="text-white underline italic"
                    >
                        View source: Food Safety Act 1990
                    </a>
                    <QueryForm
                        question={question}
                        onChange={setQuestion}
                        onSubmit={handleSubmit}
                    />
                    {isLoading && <p className="text-white">Loading...</p>}
                    {response !== null && (
                        <ResponseDisplay response={response} />
                    )}
                </div>
            </div>
        </>
    );
}

export default App;
