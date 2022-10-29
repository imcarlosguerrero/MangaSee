import concurrent.futures

def parallelFunction(*argv):
    masterFunction = argv[0]
    masterList = argv[1]
    while(len(masterList) > 0):
            try:
                if(len(argv) == 3):
                    masterWorkers = argv[2]
                    executor = concurrent.futures.ProcessPoolExecutor(max_workers = masterWorkers)
                    futures = {executor.submit(masterFunction, i): i for i in masterList}
                else:
                    masterWorkers = argv[2]
                    masterVariables = argv[3]
                    executor = concurrent.futures.ProcessPoolExecutor(max_workers = masterWorkers)
                    futures = {executor.submit(masterFunction, i, masterVariables): i for i in masterList}
                    
                for future in concurrent.futures.as_completed(futures):
                    ingreso = futures[future]
                    salida = future.result(timeout=5)
                    if(salida == True):
                        masterList.remove(ingreso)
                    else:
                        raise Exception("Error")
            except Exception as e:
                print(e)
                pass
    return True