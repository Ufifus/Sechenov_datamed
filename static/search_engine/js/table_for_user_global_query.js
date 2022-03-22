function Create() {
  const tableRef = useRef(null);
  const wrapperRef = useRef(null);

  useEffect(() => {
    const grid = new Grid({
      from: tableRef.current,
    }).render(wrapperRef.current);
  });
};

Create();