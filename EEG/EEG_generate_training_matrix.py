import os
import numpy as np
from EEG_feature_extraction import generate_feature_vectors_from_samples


def gen_training_matrix(directory_path, output_file, cols_to_ignore):

    # Initialise return matrix
    FINAL_MATRIX = None
    header = None

    for x in os.listdir(directory_path):

        # Ignore non-CSV files
        if not x.lower().endswith('.csv'):
            continue

        # Extract filename without extension
        filename = os.path.splitext(x)[0]

        # Skip files that are not 'sub_sec_0.csv' or 'sub10_sec_1.csv'
        if filename not in ['EEG_Recordings']:
            continue

        # Determine state based on filename
        #state = None
        #if 'sub_sec_0' in filename:
            #state = 0.
        #elif 'sub10_sec_1' in filename:
            #state = 1.

        print('Using file:', x)
        full_file_path = os.path.join(directory_path, x)
        vectors, new_header = generate_feature_vectors_from_samples(file_path=full_file_path,
                                                                    nsamples=150,
                                                                    period=1.,
                                                                    state=None,
                                                                    remove_redundant=True,
                                                                    cols_to_ignore=cols_to_ignore)

        if vectors is not None:
            print('Resulting vector shape for the file:', vectors.shape)
            if header is None:
                header = new_header
            else:
                # Ensure all columns have names
                if len(header) != len(new_header):
                    # Generate generic column names for additional columns
                    additional_cols = len(new_header) - len(header)
                    header += ['Column{}'.format(i) for i in range(additional_cols)]

        else:
            print('No valid feature vectors generated for the file:', x)

        if FINAL_MATRIX is None:
            FINAL_MATRIX = vectors
        else:
            FINAL_MATRIX = np.vstack([FINAL_MATRIX, vectors])

    if FINAL_MATRIX is not None:
        print('FINAL_MATRIX shape:', FINAL_MATRIX.shape)

        # Shuffle rows
        np.random.shuffle(FINAL_MATRIX)

        # Save to file
        np.savetxt(output_file, FINAL_MATRIX, delimiter=',',
                   header=','.join(header),
                   comments='')
        return None
        #print('Features saved to:', output_file)
    #else:
        #print('No valid feature vectors generated. Output file not created.')

#if __name__ == '__main__':
    #directory_path = 'C:\\Users\\SAMANTHIKA\\Desktop\\EEG_realtime\\Data\\test\\'
    #output_file = 'C:\\Users\\SAMANTHIKA\\Desktop\\EEG_realtime\\features\\out.csv'
    #gen_training_matrix(directory_path, output_file, cols_to_ignore=-1)
