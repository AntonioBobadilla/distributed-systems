#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>


typedef struct {
    unsigned char red, green, blue;
} pixel;


int main(int argc, char *argv[]) {
    int rank, size;
    char processor[MPI_MAX_PROCESSOR_NAME];
    int proc_name_len;

    // Inicializar configuracion de MPI para comenzar proceso en una maquina distinta
    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Get_processor_name(processor, &proc_name_len);



    // Establecer valores iniciales y archivo que se va a leer
    FILE *input, *output, *readings;
    input = fopen("original_image.bmp","rb");
    float red_sum = 0, green_sum = 0, blue_sum = 0;


    int y, x, i, j;
    // Leer encabezado BMP
    unsigned char header[54];
    fread(header, sizeof(unsigned char), 54, input);


    // Extraer dimensiones de la imagen
    int width = *(int*)&header[18];
    int height = *(int*)&header[22];


    // Calcular relleno de la imagen
    int padding = 0;
    while ((width * 3 + padding) % 4 != 0) {
        padding++;
    }


    // Asignar memoria para los datos de la imagen
    pixel *img_data = (pixel*)malloc(width *  height * sizeof(pixel));
    // Leer los datos de la imagen
    fread(img_data, sizeof(pixel), width * height, input);
    int num_output_files = 2;


    // Aplicar el desenfoque a la imagen en paralelo
    if (rank < size) {
        int num_procs = size - rank;
        char filename[50];
        sprintf(filename, "blurred_%d.bmp", num_procs);
        output = fopen(filename, "wb");


        // Calcular el tamaño del kernel y su sumatoria
        int kernel_size = 11 + num_procs*2;
        float kernel[kernel_size][kernel_size];
        float kernel_sum = 0;
        for (int i = 0; i < kernel_size; i++) {
            for (int j = 0; j < kernel_size; j++) {
                kernel[i][j] = 1.0 / (float)(kernel_size * kernel_size);
                kernel_sum += kernel[i][j];
            }
        }


        // Escribir el encabezado BMP
        for (int i = 0; i < 54; i++) {
            fputc(header[i], output);
        }

        // Con los primeros dos loops, se recorre toda la imagen
        // No se contemplan valores que estan en los extremos
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                total_r = 0, total_g = 0, total_b = 0;
                // Con los otros dos loops, se recorre la mascara
                // Se multiplicaran todos los valores de la mascara, 
                // por todos los pixeles que rodean el pixel que estamos analizando
                for (int i = 0; i < kernel_size; i++) {
                    for (int j = 0; j < kernel_size; j++) {
                        int nx = x - (kernel_size/2) + j;
                        int ny = y - (kernel_size/2) + i;
                        if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
                            //Multiplicacion de los pixeles con el kernel
                            int index = ny * width + nx;
                            float kernel_value = kernel[i][j] / kernel_sum;
                            total_r += kernel_value * image_data[index].r;
                            total_g += kernel_value * image_data[index].g;
                            total_b += kernel_value * image_data[index].b;
                        }
                    }
                }
                // Al final, en la copia de la imagen (el resultado), se cambiara el pixel original, por la suma calculada
                pixel blurred_pixel = {
                    (unsigned char)total_b,
                    (unsigned char)total_g,
                    (unsigned char)total_r
                };
                fputc(blurred_pixel.b, output_file);
                fputc(blurred_pixel.g, output_file);
                fputc(blurred_pixel.r, output_file);


            }
            for (int i = 0; i < padding; i++) {
                fputc(0, output_file);
            }

            //Se imprime el progreso que lleva cada proceso
            if ((y + 1) % 100 == 0) {
                printf("Processed %d rows from processor %d with a total of %d processors and image=%d from pc %s\n", y + 1, myrank, nprocs, n, processor_name);
            }
        }
        fclose(output_file);
    }
        // Clean up
        free(image_data);
        fclose(input_file);
        MPI_Finalize();
    return 0;
}
