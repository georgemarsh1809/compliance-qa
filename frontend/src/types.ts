export type QueryRequest = {
    question: string;
};

export type Source = {
    page: number | null;
    text: string;
};

export type QueryResponse = {
    answer: string;
    sources: Source[];
};
