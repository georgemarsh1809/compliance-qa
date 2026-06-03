import type { Source } from '../types';

type SourceCardProps = {
    source: Source;
};

export const SourceCard = ({ source }: SourceCardProps) => {
    return (
        <div className="bg-slate-800 rounded p-4 text-white">
            {source.page !== null ? (
                <span className="text-slate-400 text-sm">
                    Page: {source.page}
                </span>
            ) : (
                <span className="text-slate-400 text-sm">Unknown Page</span>
            )}
            <p className="mt-2">{source.text}</p>
        </div>
    );
};
