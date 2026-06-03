type QueryFormProps = {
    question: string;
    onSubmit: (newValue: string) => void;
    onChange: (value: string) => void;
};

export const QueryForm = ({ question, onSubmit, onChange }: QueryFormProps) => {
    return (
        <div className="flex gap-4 w-full">
            <input
                className="bg-slate-800 text-white border border-slate-600 rounded px-4 py-2 w-full"
                value={question}
                onChange={(e) => {
                    onChange(e.target.value);
                }}
                placeholder="Ask a question..."
            ></input>
            <button
                className="text-slate-900 bg-white cursor-pointer rounded px-2"
                onClick={() => onSubmit(question)}
            >
                Submit
            </button>
        </div>
    );
};
