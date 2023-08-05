package main

import (
	"log"

	huggingfaceinternal "github.com/nlpodyssey/spago/cmd/huggingfaceimporter/internal"
)

func main() {
	modelDir, modelName := "./model", "j-hartmann/emotion-english-distilroberta-base"
	importer := huggingfaceinternal.NewImporterArgs(modelDir, modelName, huggingfaceinternal.DefaultModelsURL, false)

	err := importer.RunImporter()
	if err != nil {
		log.Fatal(err)
	}
}
