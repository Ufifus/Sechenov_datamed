var datatable = progress.data; //сюда вывод в консоль пока что для тестов
        if (datatable == null){
            console.log('clear');
        } else  {
            const id_data = datatable.PMID;
            const element = progressDataTableElement.querySelector('[id="' +id_data+ '"]') || false;
            if (element == false){
                const html = `
                  <tr id=${datatable.PMID}>
                    <td>${datatable.PMID}</td>
                    <td>${datatable.title}</td>
                    <td>${datatable.author}</td>
                    <td>${datatable.place}</td>
                  </tr>`
                $('#tasks').append(html);
                console.log('yes');
                console.log(element);

                container = document.getElementById('wrapper')
                
            }
        }