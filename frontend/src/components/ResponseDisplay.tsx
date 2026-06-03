import type { QueryResponse } from '../types';
import { SourceCard } from './SourceCard';
import Markdown from 'react-markdown';

type ResponseDisplayProps = {
    response: QueryResponse;
};

export const ResponseDisplay = ({ response }: ResponseDisplayProps) => {
    return (
        <div className="mt-8 text-white ">
            <div>
                <Markdown
                    components={{
                        h1: ({ children }) => (
                            <h1 className="text-white font-semibold text-xl mt-4 mb-2">
                                {children}
                            </h1>
                        ),
                        h2: ({ children }) => (
                            <h2 className="text-white font-semibold text-xl mt-4 mb-2">
                                {children}
                            </h2>
                        ),
                        p: ({ children }) => (
                            <p className="text-slate-200 mb-3 leading-relaxed">
                                {children}
                            </p>
                        ),
                        strong: ({ children }) => (
                            <strong className="text-white font-semibold">
                                {children}
                            </strong>
                        ),
                    }}
                >
                    {response.answer}
                </Markdown>
            </div>
            <div className="mt-6 flex flex-col gap-4">
                Sources:
                {response.sources.map((source, index) => (
                    <SourceCard key={index} source={source} />
                ))}
            </div>
        </div>
    );
};
