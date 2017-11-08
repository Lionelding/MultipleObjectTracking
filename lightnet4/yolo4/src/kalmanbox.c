#include "opencv2/core/types_c.h"
#include "opencv2/video/tracking.hpp"
#include "opencv2/legacy/compat.hpp"
#include "opencv2/core/mat.hpp"
#include "kalmanbox.h"

#define CVX_YELLOW	CV_RGB(0xff,0xff,0x00)
#define CVX_WHITE	CV_RGB(0xff,0xff,0xff)
#define CVX_RED		CV_RGB(0xff,0x00,0x00)


kalmanbox* create_kalmanfilter(CvPoint boxcenter, CvPoint boxvelocity){

    float state[4]={boxcenter.x, boxcenter.y,boxvelocity.x,boxvelocity.y};
    float state2[2]={boxcenter.x, boxcenter.y};
    float state3[4]={boxcenter.x+10, boxcenter.y-10, boxvelocity.x,boxvelocity.y};

	kalmanbox* kalmanbox_out = (kalmanbox*)malloc(sizeof(kalmanbox));
	kalmanbox_out->kalmanfilter=cvCreateKalman(4,2,0);
	kalmanbox_out->x_k = cvCreateMat(4, 1, CV_32FC1 );
	memcpy(kalmanbox_out->x_k->data.fl, state, sizeof(state));

    CvRandState rng;
    cvRandInit( &rng, 0, 1, -1, CV_RAND_UNI );
    cvRandSetRange( &rng, 0, 0, 0 );
    rng.disttype = CV_RAND_NORMAL;


    kalmanbox_out->z_k = cvCreateMat( 2, 1, CV_32FC1 );
    cvZero(kalmanbox_out->z_k );
    memcpy(kalmanbox_out->z_k->data.fl, state2, sizeof(state2));
    printf("\t Measurement State z_k x: %0.0f, y: %0.0f\n", kalmanbox_out->z_k->data.fl[0], kalmanbox_out->z_k->data.fl[1]);


    //TODO:modify the time
    float dt=1;
    const float trans_data[16]={1,0,dt,0,0,1,0,dt,0,0,1,0,0,0,0,1};
    memcpy( kalmanbox_out->kalmanfilter->transition_matrix->data.fl, trans_data, sizeof(trans_data));

    cvSetIdentity( kalmanbox_out->kalmanfilter->measurement_matrix, cvRealScalar(1) );
    cvSetIdentity( kalmanbox_out->kalmanfilter->process_noise_cov, cvRealScalar(1e-4) ); //Q --> 'process noise covariance matrix
    cvSetIdentity( kalmanbox_out->kalmanfilter->measurement_noise_cov, cvRealScalar(1e-3) ); //R --> measurement noise covariance matrix
    cvSetIdentity( kalmanbox_out->kalmanfilter->error_cov_post, cvRealScalar(0.1));
    cvRand(&rng, kalmanbox_out->kalmanfilter->state_post);

    memcpy(kalmanbox_out->kalmanfilter->PriorState, state3, sizeof(state2));


    printf("\t PriorState x: %0.0f, y: %0.0f, vx: %0.0f, vy: %0.0f\n", kalmanbox_out->kalmanfilter->PriorState[0], kalmanbox_out->kalmanfilter->PriorState[1], kalmanbox_out->kalmanfilter->PriorState[2], kalmanbox_out->kalmanfilter->PriorState[3]);
    printf("\t state_post x: %0.0f, y: %0.0f, vx: %0.0f, vy: %0.0f\n", kalmanbox_out->kalmanfilter->state_post->data.fl[0], kalmanbox_out->kalmanfilter->state_post->data.fl[1], kalmanbox_out->kalmanfilter->state_post->data.fl[2], kalmanbox_out->kalmanfilter->state_post->data.fl[3]);

    //memcpy(kalmanbox_out->kalmanfilter->state_pre, state3, sizeof(state2));

//    memcpy(kalmanbox_out->kalmanfilter->MeasurementMatr, state2, sizeof(state2));
//    memcpy(kalmanbox_out->kalmanfilter->measurement_matrix->data.fl, state2, sizeof(state2));

    const CvMat* y_k = cvKalmanPredict(kalmanbox_out->kalmanfilter, 0 );
    printf("\t Predicted State y_k x: %0.0f, y: %0.0f, vx: %0.0f, vy: %0.0f\n", y_k->data.fl[0], y_k->data.fl[1], y_k->data.fl[2], y_k->data.fl[3]);

	const CvMat* temp=cvKalmanCorrect(kalmanbox_out->kalmanfilter, kalmanbox_out->z_k );
	memcpy(kalmanbox_out->x_k->data.fl, temp->data.fl, sizeof(temp));
	printf("\t Updated State x_k x: %0.0f, y: %0.0f, vx: %0.0f, vy: %0.0f\n", kalmanbox_out->x_k->data.fl[0], kalmanbox_out->x_k->data.fl[1], kalmanbox_out->x_k->data.fl[2], kalmanbox_out->x_k->data.fl[3]);

    return kalmanbox_out;
}

CvMat* update_kalmanfilter(IplImage *im_frame, kalmanbox* kalmanbox_out, CvPoint observedPt, CvPoint observedV, int width, int height){


//	float state[4]={observedPt.x-10, observedPt.y+10,observedV.x,observedV.y};
//	memcpy(kalmanbox_out->x_k->data.fl, state, sizeof(state));


 	//printf("\t Bouding Box Measured Center x: %i, y: %i, vx: %i, vy: %i\n", observedPt.x, observedPt.y, observedV.x, observedV.y);
	printf("\t Previous Measurement z_k x: %0.0f, y: %0.0f\n", kalmanbox_out->z_k->data.fl[0], kalmanbox_out->z_k->data.fl[1]);
	printf("\t Previous State x_k x: %0.0f, y: %0.0f\n", kalmanbox_out->x_k->data.fl[0], kalmanbox_out->x_k->data.fl[1]);

	float observed_position[2]={observedPt.x, observedPt.y};
	memcpy(kalmanbox_out->z_k->data.fl, observed_position, sizeof(observed_position));
	printf("\t Current Measurement z_k x: %0.0f, y: %0.0f\n", kalmanbox_out->z_k->data.fl[0], kalmanbox_out->z_k->data.fl[1]);

//	const CvMat* y_k = cvKalmanPredict(kalmanbox_out->kalmanfilter, 0 );
//	printf("\t Predicted State y_k x: %0.0f, y: %0.0f, vx: %0.0f, vy: %0.0f\n", y_k->data.fl[0], y_k->data.fl[1], y_k->data.fl[2], y_k->data.fl[3]);


	const CvMat* y_k = cvKalmanPredict(kalmanbox_out->kalmanfilter, 0 );
	printf("\t Predicted State y_k x: %0.0f, y: %0.0f, vx: %0.0f, vy: %0.0f\n", y_k->data.fl[0], y_k->data.fl[1], y_k->data.fl[2], y_k->data.fl[3]);

	float px=CV_MAT_ELEM(*y_k, float, 0, 0);
	float py=CV_MAT_ELEM(*y_k, float, 1, 0);
	CvPoint predictedlefttop=cvPoint(px-width/2, py-height/2);
	CvPoint predictedrightbot=cvPoint(px+width/2, py+height/2);
	cvRectangle(im_frame, predictedlefttop, predictedrightbot, CVX_WHITE, 3, 8, 0 );



	float rx=CV_MAT_ELEM(*(kalmanbox_out->x_k), float, 0, 0);
	float ry=CV_MAT_ELEM(*(kalmanbox_out->x_k), float, 1, 0);
	CvPoint reallefttop=cvPoint(rx-width/2, ry-height/2);
	CvPoint realrightbot=cvPoint(rx+width/2, ry+height/2);
	cvRectangle(im_frame, reallefttop, realrightbot, CVX_RED, 3, 8, 0 );


	const CvMat* temp=cvKalmanCorrect(kalmanbox_out->kalmanfilter, kalmanbox_out->z_k );
	memcpy(kalmanbox_out->x_k->data.fl, temp->data.fl, sizeof(temp));
	printf("\t Updated State x_k x: %0.0f, y: %0.0f, vx: %0.0f, vy: %0.0f\n", kalmanbox_out->x_k->data.fl[0], kalmanbox_out->x_k->data.fl[1], kalmanbox_out->x_k->data.fl[2], kalmanbox_out->x_k->data.fl[3]);
    printf("\t state_post x: %0.0f, y: %0.0f, vx: %0.0f, vy: %0.0f\n", kalmanbox_out->kalmanfilter->state_post->data.fl[0], kalmanbox_out->kalmanfilter->state_post->data.fl[1], kalmanbox_out->kalmanfilter->state_post->data.fl[2], kalmanbox_out->kalmanfilter->state_post->data.fl[3]);



	return y_k;
}
